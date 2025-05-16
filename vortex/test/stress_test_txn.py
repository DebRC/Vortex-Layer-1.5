from web3 import Web3
from random import choice
from concurrent.futures import ThreadPoolExecutor
import time
import csv
import os
import subprocess
import threading

from dotenv import load_dotenv
load_dotenv("../.env")

# Settings
NUM_CALLS_DICT = {
    "15M": 3500,
    "30M": 7000,
    "45M": 10500,
    "60M": 14000,
    "75M": 17500,
    "90M": 21000,
    "105M": 24500,
    "120M": 28000,
    "135M": 31500,
    "150M": 35000,
    "200M": 42000,
    "250M": 52500,
    "300M": 63000,
    "350M": 73500,
    "400M": 84000,
    "450M": 94500,
    "500M": 105000,
}
RPC_URL = os.getenv("RPC_URL")
NUMBER_OF_CALLS = NUM_CALLS_DICT["15M"]
NODE_IPC_PATH = os.getenv("NODE_IPC_PATH")
CPU_PROFILE_INTERVAL = int(os.getenv("CPU_PROFILE_INTERVAL"))
CPU_PROFILE_COUNT = int(os.getenv("CPU_PROFILE_COUNT"))
READINGS_DIR = os.getenv("READINGS_DIR")
os.makedirs(READINGS_DIR, exist_ok=True)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Ethereum node connection failed")
w3_ipc = Web3(Web3.IPCProvider(NODE_IPC_PATH))

if not w3.is_connected() or not w3_ipc.is_connected():
    raise Exception("Ethereum node connection failed")

private_keys = [
    os.getenv("PRIVATE_KEY_1"),
    os.getenv("PRIVATE_KEY_2"),
    os.getenv("PRIVATE_KEY_3"),
]

sender_key = choice(private_keys)
receiver_key = choice(private_keys)
while sender_key == receiver_key:
    receiver_key = choice(private_keys)

sender_account = w3.eth.account.from_key(sender_key)
receiver_account = w3.eth.account.from_key(receiver_key)
nonce_start = w3.eth.get_transaction_count(sender_account.address, "pending")

print(f"Sending {NUMBER_OF_CALLS} txns from {sender_account.address} to {receiver_account.address}")

cpu_profile_files = []
txn_records = []


def run_cpu_profiler(profile_id):
    abs_prof = os.path.abspath(os.path.join(READINGS_DIR, f"cpu_{profile_id}.prof"))
    cpu_profile_files.append(abs_prof)
    subprocess.run(["geth", "--exec", f"debug.startCPUProfile('{abs_prof}')", "attach", NODE_IPC_PATH])
    time.sleep(CPU_PROFILE_INTERVAL)
    subprocess.run(["geth", "--exec", "debug.stopCPUProfile()", "attach", NODE_IPC_PATH])

def profiler_scheduler():
    for i in range(CPU_PROFILE_COUNT):
        run_cpu_profiler(i)

# Pre-sign all transactions
# base_fee = w3.eth.get_block("pending").baseFeePerGas
base_fee = w3.to_wei(10, 'gwei')
tip = w3.to_wei(2, 'gwei')
max_fee = int(base_fee) + tip

signed_txns = []
for i in range(NUMBER_OF_CALLS):
    txn = {
        'nonce': nonce_start + i,
        'to': receiver_account.address,
        'value': w3.to_wei(0.1, 'ether'),
        'gas': 21000,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': tip,
        'chainId': 32382,
        'type': '0x2'
    }
    signed = w3.eth.account.sign_transaction(txn, sender_key)
    signed_txns.append((signed, txn['nonce']))

threading.Thread(target=profiler_scheduler, daemon=True).start()
start_block = w3.eth.block_number+1
print(f"Start Block: {start_block}")
tx_hash_list = []

# Burst send all signed txns
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(w3.eth.send_raw_transaction, signed.raw_transaction) for signed, _ in signed_txns]
    for i, future in enumerate(futures):
        try:
            tx_hash = future.result()
            print(f"Sent: {tx_hash.hex()} Nonce: {signed_txns[i][1]}")
            tx_hash_list.append((tx_hash.hex(), signed_txns[i][1]))
        except Exception as e:
            print(f"Error sending tx {i}: {e}")

print(f"{len(tx_hash_list)} txns sent. Waiting for confirmations...")

for tx_hash, nonce in tx_hash_list:
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        print(f"Confirmed {tx_hash} in block {receipt.blockNumber}")
    except:
        print(f"Timeout or error for tx {tx_hash}")

end_block = w3.eth.block_number
print(f"End Block: {end_block}")

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
