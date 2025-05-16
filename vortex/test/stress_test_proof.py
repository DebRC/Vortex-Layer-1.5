import os, random, time
import json
import subprocess
from web3 import Web3
from eth_account import Account
from concurrent.futures import ThreadPoolExecutor
import threading
import csv

from dotenv import load_dotenv
load_dotenv("../.env")

NUM_CALLS_DICT = {
    "15M": 150,
    "30M": 300,
    "45M": 450,
    "60M": 600,
    "75M": 750,
    "90M": 900,
    "105M": 1050,
    "120M": 1200,
}

# Configuration
NUMBER_OF_CALLS = NUM_CALLS_DICT[os.getenv("GAS_LIMIT")]
NODE_IPC_PATH = os.getenv("NODE_IPC_PATH")
CPU_PROFILE_INTERVAL = int(os.getenv("CPU_PROFILE_INTERVAL"))
CPU_PROFILE_COUNT = int(os.getenv("CPU_PROFILE_COUNT"))
READINGS_DIR = os.getenv("READINGS_DIR")
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("VERIFIER_CONTRACT_ADDRESS")
ABI_PATH = os.getenv("VERIFIER_ABI_PATH")
BUILD_DIR = os.getenv("BUILD_DIR")
PROOFS_DIR = os.path.join(BUILD_DIR, "proofs")
CIRCUIT_NAME = os.getenv("ZK_CIRCUIT_NAME")
PRIVATE_KEY = random.choice([os.getenv("PRIVATE_KEY_1"),
    os.getenv("PRIVATE_KEY_2"),
    os.getenv("PRIVATE_KEY_3"),])
os.makedirs(READINGS_DIR, exist_ok=True)
os.makedirs(PROOFS_DIR, exist_ok=True)

# Load ABI
with open(ABI_PATH) as f:
    ABI = json.load(f)['abi']

# Setup Web3 and contract
w3 = Web3(Web3.HTTPProvider(RPC_URL))
acct = Account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

cpu_profile_files = []

def cached_proof_path(i):
    """Return folder path for proof #i."""
    p = os.path.join(PROOFS_DIR, str(i))
    os.makedirs(p, exist_ok=True)
    return p

def run_cpu_profiler(idx):
    prof = os.path.abspath(os.path.join(READINGS_DIR, f"cpu_{idx}.prof"))
    cpu_profile_files.append(prof)
    # Try to start profiling; if already running, skip
    try:
        subprocess.run(
            ["geth", "--exec", f"debug.startCPUProfile('{prof}')", "attach", NODE_IPC_PATH]
        )
    except subprocess.CalledProcessError as e:
        if "CPU profiling already in progress" in e.stderr:
            print(f"⚠️  Profiler #{idx}: already in progress, skipping start")
        else:
            raise
    # Wait the interval
    time.sleep(CPU_PROFILE_INTERVAL)
    # Try to stop profiling; if none running, skip
    try:
        subprocess.run(
            ["geth", "--exec", "debug.stopCPUProfile()", "attach", NODE_IPC_PATH]
        )
    except subprocess.CalledProcessError as e:
        if "no CPU profiling in progress" in e.stderr.lower():
            print(f"⚠️  Profiler #{idx}: no active session, skipping stop")
        else:
            raise

def profiler_scheduler():
    for i in range(CPU_PROFILE_COUNT):
        run_cpu_profiler(i)

def run_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        raise Exception("Command failed")
    return result.stdout

def create_proof(i):
    dst = cached_proof_path(i)
    proof_json = os.path.join(dst, "proof.json")
    public_json = os.path.join(dst, "public.json")
    
    if os.path.isfile(proof_json) and os.path.isfile(public_json):
        print(f"♻️  Reusing cached proof #{i}")
    else:
        inp = {
            "leaf": str(i + 1000),
            "pathElements": ["0"] * 20,
            "pathIndices": ["0"] * 20
        }
        inp_path = os.path.join(BUILD_DIR, "input.json")
        with open(inp_path, "w") as f:
            json.dump(inp, f)
        run_command([
            "node",
            os.path.join(BUILD_DIR, f"{CIRCUIT_NAME}_js", "generate_witness.js"),
            os.path.join(BUILD_DIR, f"{CIRCUIT_NAME}_js", f"{CIRCUIT_NAME}.wasm"),
            inp_path,
            os.path.join(BUILD_DIR, "witness.wtns")
        ])
        
        cmd = [
            "snarkjs", "groth16", "prove",
            os.path.join(BUILD_DIR, f"{CIRCUIT_NAME}.zkey"),
            os.path.join(BUILD_DIR, "witness.wtns"),
            proof_json,
            public_json
        ]
        run_command(cmd)

def sign_proof(nonce):
    proof  = json.load(open(os.path.join(BUILD_DIR, "proof.json")))
    public = json.load(open(os.path.join(BUILD_DIR, "public.json")))

    pi_a = [
        int(proof["pi_a"][0]),
        int(proof["pi_a"][1]),
    ]
    pi_b = [
        [int(proof["pi_b"][0][0]), int(proof["pi_b"][0][1])],
        [int(proof["pi_b"][1][0]), int(proof["pi_b"][1][1])],
    ]
    pi_c = [
        int(proof["pi_c"][0]),
        int(proof["pi_c"][1]),
    ]
    pub_signals = [
        int(public[0]),
    ]

    
    base_fee = w3.to_wei(10, 'gwei')
    tip = w3.to_wei(2, 'gwei')
    max_fee = int(base_fee) + tip

    tx = contract.functions.verifyProof(pi_a, pi_b, pi_c, pub_signals).build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "gas": 500000,
        "maxFeePerGas": max_fee,
        "maxPriorityFeePerGas": tip,
    })
    return acct.sign_transaction(tx)

def generate_and_sign_proof(NUMBER_OF_CALLS):
    signed_txns = []
    base_nonce = w3.eth.get_transaction_count(acct.address, "pending")
    for i in range(NUMBER_OF_CALLS):
        print(f"🔧 Generating proof #{i} (leaf={i+1000})")
        create_proof(i)
        signed_txns.append(sign_proof(base_nonce + i))
    return signed_txns    

def submit_proof(signed_txns):
    tx_hash_list = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(w3.eth.send_raw_transaction, signed_tx.raw_transaction) for signed_tx in signed_txns]
        for future in futures:
            try:
                tx_hash = future.result()
                tx_hash_list.append(tx_hash)
                print(f"✅ Proof submitted: {tx_hash.hex()}")
            except Exception as e:
                print(f"❌ Error submitting proof: {e}")
    print("All proofs submitted. Waiting for confirmations...")
    return tx_hash_list

def confirm_proofs(tx_hash_list):
    for tx_hash in tx_hash_list:
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            print(f"Confirmed {tx_hash.hex()} in block {receipt.blockNumber}")
        except Exception as e:
            print(f"❌ Timeout or error for tx {tx_hash.hex()}: {e}")
    print("All proofs confirmed.")

def generate_results(start_block, end_block):
    # CPU usage summary
    cpu_total = 0
    cpu_count = 0
    cpu_usage = []
    for prof_file in cpu_profile_files[1:]:
        result = subprocess.run(["go", "tool", "pprof", "-top", prof_file], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if line.strip().startswith("Duration:"):
                try:
                    sec = float(line.strip().split()[5].replace("s", ""))
                    cpu_total += sec
                    cpu_count += 1
                    cpu_usage.append({"profileNumber": str(cpu_count), "CPUUsage(%)": str(sec*100/CPU_PROFILE_INTERVAL)})
                    break
                except:
                    pass
    with open(os.path.join(READINGS_DIR, "cpu_details.csv"), "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["profileNumber", "CPUUsage(%)"])
        writer.writeheader()
        writer.writerows(cpu_usage)  
        
    # Block-based TPS + block details
    block_details = []
    # Step 1: Fetch all blocks first
    for blk in range(start_block, end_block + 1):
        block = w3.eth.get_block(blk, full_transactions=True)
        tx_count = len(block.transactions)
        gas_used = block.gasUsed
        base_fee = block.get("baseFeePerGas", 0)
        block_details.append({
            "blockNumber": blk,
            "gasUsed": gas_used,
            "baseFeePerGas": base_fee,
            "txCount": tx_count
        })
    # Step 2: Trim leading and trailing 0-tx blocks
    while block_details and block_details[0]["txCount"] == 0:
        block_details.pop(0)
    while block_details and block_details[-1]["txCount"] == 0:
        block_details.pop()
    # Step 3: Now compute totals only from trimmed list
    block_count = len(block_details)
    block_gas_total = sum(b["gasUsed"] for b in block_details)
    missed_blocks = sum(b["gasUsed"]==0 for b in block_details)

    with open(os.path.join(READINGS_DIR, "block_details.csv"), "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["blockNumber", "gasUsed", "baseFeePerGas", "txCount"])
        writer.writeheader()
        writer.writerows(block_details)

    block_tps = block_gas_total / (block_count*CPU_PROFILE_INTERVAL) if block_count > 0 else 0
    
    print("======== FINAL REPORT ========")
    print(f"Blocks Used: {block_count}")
    print(f"Total Gas in Blocks: {block_gas_total}")
    print(f"Gas-Based TPS: {block_tps:.2f}")
    print(f"Missed Blocks: {missed_blocks}")
    print(f"CPU Average Usage: {((cpu_total / cpu_count)/CPU_PROFILE_INTERVAL)*100:.2f}%" if cpu_count > 0 else "CPU Average Usage: N/A")
    print("======== END ========")
                        
def main():
    signed_txns = generate_and_sign_proof(NUMBER_OF_CALLS)
    threading.Thread(target=profiler_scheduler, daemon=True).start()
    start_block = w3.eth.block_number+1
    tx_hash_list = submit_proof(signed_txns)
    confirm_proofs(tx_hash_list)
    end_block = w3.eth.block_number
    generate_results(start_block, end_block)
    
if __name__ == "__main__":
    main()
