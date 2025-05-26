import os, random
import json
import subprocess
from web3 import Web3
from eth_account import Account
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

from dotenv import load_dotenv

load_dotenv("../.env")

PER_TXN_GAS = int(os.getenv("PER_TXN_GAS"))
ESTIMATED_BLOCKS_TO_MONITOR = int(os.getenv("ESTIMATED_BLOCKS_TO_MONITOR"))
NUM_PROOFS = 10
PROFILING_NODE_IPC_PATH = os.getenv("PROFILING_NODE_IPC_PATH")
PROFILING_NODE_LOG = os.getenv("PROFILING_NODE_LOG")
SLOT_DURATION = int(os.getenv("CPU_PROFILE_INTERVAL"))
READINGS_DIR = os.getenv("READINGS_DIR")
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("VORTEX_CONTRACT_ADDRESS")
ABI_PATH = os.getenv("VORTEX_ABI_PATH")
BUILD_DIR = os.getenv("BUILD_DIR")
PROOFS_DIR = os.path.join(BUILD_DIR, "proofs")
CIRCUIT_NAME = os.getenv("ZK_CIRCUIT_NAME")
PRIVATE_KEY = random.choice(
    [
        os.getenv("PRIVATE_KEY_1"),
        os.getenv("PRIVATE_KEY_2"),
        os.getenv("PRIVATE_KEY_3"),
    ]
)
os.makedirs(READINGS_DIR, exist_ok=True)
os.makedirs(PROOFS_DIR, exist_ok=True)
DEVNULL = subprocess.DEVNULL

with open(ABI_PATH) as f:
    ABI = json.load(f)["abi"]

# Setup Web3 and contract
w3 = Web3(Web3.HTTPProvider(RPC_URL))
acct = Account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

cpu_profile_file = ''

def run_command(cmd):
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        print(f"Error :: {result.stderr}")
        raise Exception("Command failed")
    return result.stdout

def start_cpu_profiling():
    abs_prof = os.path.abspath(
        os.path.join(READINGS_DIR, f"cpu.prof")
    )
    global cpu_profile_file
    cpu_profile_file = abs_prof

    subprocess.run([
        "geth",
        "--exec", "try { debug.stopCPUProfile(); } catch (e) {}",
        "attach", PROFILING_NODE_IPC_PATH
    ], check=False, stdout=DEVNULL, stderr=DEVNULL)

    subprocess.run([
        "geth",
        "--exec", f'debug.startCPUProfile("{abs_prof}")',
        "attach", PROFILING_NODE_IPC_PATH
    ], check=True, stdout=DEVNULL, stderr=DEVNULL)

def stop_cpu_profiling():
    subprocess.run([
        "geth",
        "--exec", "debug.stopCPUProfile()",
        "attach", PROFILING_NODE_IPC_PATH
    ], check=True, stdout=DEVNULL, stderr=DEVNULL)

def get_proof_path(i):
    p = os.path.join(PROOFS_DIR, str(i))
    os.makedirs(p, exist_ok=True)
    return p

def sign_proof(proofID, nonce):
    proof_folder = get_proof_path(proofID)
    proof = json.load(open(os.path.join(proof_folder, "proof.json")))
    public = json.load(open(os.path.join(proof_folder, "public.json")))

    pi_a = [int(proof["pi_a"][0]), int(proof["pi_a"][1])]
    pi_b = [
        [int(proof["pi_b"][0][0]), int(proof["pi_b"][0][1])],
        [int(proof["pi_b"][1][0]), int(proof["pi_b"][1][1])],
    ]
    pi_c = [int(proof["pi_c"][0]), int(proof["pi_c"][1])]
    pub_signals = [int(x) for x in public]

    base_fee = w3.to_wei(10, "gwei")
    tip = w3.to_wei(2, "gwei")
    max_fee = int(base_fee) + tip

    fn = contract.functions.announceProof(pi_a, pi_b, pi_c, pub_signals)
    est = fn.estimate_gas({"from": acct.address})

    print(f"Estimated Gas for Proof {proofID} :: {est}, Nonce :: {nonce}")

    tx = fn.build_transaction(
        {
            "from": acct.address,
            "nonce": nonce,
            "gas": est,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": tip,
        }
    )
    return proofID, acct.sign_transaction(tx)

def sign_proofs(NUMBER_OF_CALLS):
    signed_txns = []
    base_nonce = w3.eth.get_transaction_count(acct.address, "pending")
    for i in range(NUMBER_OF_CALLS):
        signed_txns.append(sign_proof(i, base_nonce + i))
    return signed_txns

def submit_proofs(signed_txns):
    tx_hash_list = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_id = {
            executor.submit(w3.eth.send_raw_transaction, signed_tx.raw_transaction): proofID
            for proofID, signed_tx in signed_txns
        }

        for future in as_completed(future_to_id):
            proofID = future_to_id[future]
            try:
                tx_hash = future.result()
                tx_hash_list.append((proofID,tx_hash))
                print(f"Proof {proofID} Submitted :: 0x{tx_hash.hex()}")
            except Exception as e:
                print(f"Error Submitting Proof {proofID}: {e}")

    return tx_hash_list

def confirm_proofs(tx_hash_list):
    confirmed_proofs=0
    for proofID, tx_hash in tx_hash_list:
        try:
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            print(f"Proof {proofID} Confirmed (Not Verified) :: 0x{tx_hash.hex()}, Gas Used :: {receipt.gasUsed}, Block :: {receipt.blockNumber}")
            confirmed_proofs+=1
        except Exception as e:
            print(f"Proof {proofID} Timeout or Error :: 0x{tx_hash.hex()}\n{e}")
    print(f"{confirmed_proofs} Proofs Confirmed.")

def main():
    signed_txns = sign_proofs(NUM_PROOFS)
    start_block = w3.eth.block_number + 1
    tx_hash_list = submit_proofs(signed_txns)
    confirm_proofs(tx_hash_list)
    end_block = w3.eth.block_number
    # generate_results(start_block, end_block)

if __name__ == "__main__":
    main()
