from web3 import Web3
from random import choice
from concurrent.futures import ThreadPoolExecutor
import time
import csv
import os
import subprocess
import threading

# Settings
NUMBER_OF_CALLS = 5000
NODE_IPC_PATH = "../network/node-0/execution/geth.ipc"
CPU_PROFILE_INTERVAL = 12
CPU_PROFILE_COUNT = 5
READINGS_DIR = "../readings"
os.makedirs(READINGS_DIR, exist_ok=True)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8000'))
w3_ipc = Web3(Web3.IPCProvider(NODE_IPC_PATH))

if not w3.is_connected() or not w3_ipc.is_connected():
    raise Exception("Ethereum node connection failed")

private_keys = [
    "0xebe6b156b76ade1def420429479acaaaff4b761ddc9888e710a7f1a7cc4d5c81",
    "640798ca3f30dfd01eb1ab3d145ef08c1cff9009037015a6812351f63a07835e",
    "3b24a5a6c44b9a026c481bfa48849cf2732d117f63de55eaf631812738628cc7"
]

sender_key = choice(private_keys)
receiver_key = choice(private_keys)
while sender_key == receiver_key:
    receiver_key = choice(private_keys)

sender_account = w3.eth.account.from_key(sender_key)
receiver_account = w3.eth.account.from_key(receiver_key)
nonce_start = w3.eth.get_transaction_count(sender_account.address, "pending")

print(f"Sending {NUMBER_OF_CALLS} txns from {sender_account.address} to {receiver_account.address}")

start_block = w3.eth.block_number
print(f"Start Block: {start_block}")

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

threading.Thread(target=profiler_scheduler, daemon=True).start()

def send_transaction(nonce):
    try:
        base_fee = w3.eth.get_block("pending").baseFeePerGas
        tip = w3.to_wei(2, 'gwei')
        max_fee = int(base_fee * 1.5) + tip

        txn = {
            'nonce': nonce,
            'to': receiver_account.address,
            'value': w3.to_wei(0.1, 'ether'),
            'gas': 21000,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': tip,
            'chainId': 32382,
            'type': '0x2'
        }

        signed = w3.eth.account.sign_transaction(txn, sender_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"Sent: {tx_hash.hex()} Nonce: {nonce}")
        return (tx_hash.hex(), nonce)
    except Exception as e:
        print(f"Error at nonce {nonce}: {e}")
        return (None, nonce)

start_time = time.time()
tx_hash_list = []

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(send_transaction, nonce_start + i) for i in range(NUMBER_OF_CALLS)]
    for future in futures:
        result = future.result()
        if result[0]:
            tx_hash_list.append(result)

print(f"{len(tx_hash_list)} txns sent. Waiting for confirmations...")

for tx_hash, nonce in tx_hash_list:
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        print(f"Confirmed {tx_hash} in block {receipt.blockNumber}")
        txn_records.append({
            "hash": tx_hash,
            "nonce": nonce,
            "blockNumber": receipt.blockNumber,
            "status": receipt.status
        })
    except:
        print(f"Timeout or error for tx {tx_hash}")

end_block = w3.eth.block_number
print(f"End Block: {end_block}")

# Save txn report
with open(os.path.join(READINGS_DIR, "txn_report.csv"), "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["hash", "nonce", "blockNumber", "status"])
    writer.writeheader()
    writer.writerows(txn_records)

# CPU usage summary
cpu_total = 0
cpu_count = 0
for prof_file in cpu_profile_files[1:]:
    result = subprocess.run(["go", "tool", "pprof", "-top", prof_file], stdout=subprocess.PIPE, text=True)
    for line in result.stdout.splitlines():
        if line.strip().startswith("Duration:"):
            try:
                sec = float(line.strip().split()[5].replace("s", ""))
                cpu_total += sec
                cpu_count += 1
                break
            except:
                pass

with open(os.path.join(READINGS_DIR, "cpu_usage_summary.txt"), "w") as f:
    f.write(f"Profiles: {cpu_count}\n")
    f.write(f"Total CPU Usage: {cpu_total:.2f} sec\n")
    if cpu_count > 0:
        f.write(f"Average CPU Usage: {((cpu_total / cpu_count)/CPU_PROFILE_INTERVAL)*100:.2f}%\n")
    else:
        f.write("Average CPU Usage: N/A (no valid profiles)\n")

# Block-based TPS + block details
block_tx_total = 0
block_count = 0
block_details = []

for blk in range(start_block + 1, end_block + 1):
    block = w3.eth.get_block(blk, full_transactions=True)
    gas_used = block.gasUsed
    base_fee = block.get("baseFeePerGas", 0)
    tx_count = len(block.transactions)
    block_tx_total += tx_count
    block_count += 1
    print(f"[Block {blk}] Gas Used: {gas_used} | Base Fee: {base_fee} | Txns: {tx_count}")
    block_details.append({
        "blockNumber": blk,
        "gasUsed": gas_used,
        "baseFeePerGas": base_fee,
        "txCount": tx_count
    })

with open(os.path.join(READINGS_DIR, "block_details.csv"), "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["blockNumber", "gasUsed", "baseFeePerGas", "txCount"])
    writer.writeheader()
    writer.writerows(block_details)

block_tps = block_tx_total / (block_count*CPU_PROFILE_INTERVAL) if block_count > 0 else 0

print("======== FINAL REPORT ========")
print(f"Blocks Used: {block_count}")
print(f"Total Txns in Blocks: {block_tx_total}")
print(f"Block-Based TPS: {block_tps:.2f}")
print(f"CPU Average Usage: {((cpu_total / cpu_count)/CPU_PROFILE_INTERVAL)*100:.2f}%" if cpu_count > 0 else "CPU Average Usage: N/A")
print("======== END ========")
