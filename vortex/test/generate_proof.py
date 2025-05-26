import json
import os
import random
import secrets
import subprocess
from dotenv import load_dotenv

load_dotenv("../.env")

BUILD_DIR = os.getenv("BUILD_DIR")
PROOFS_DIR = os.path.join(BUILD_DIR, "proofs")
CIRCUIT_NAME = os.getenv("ZK_CIRCUIT_NAME")
os.makedirs(PROOFS_DIR, exist_ok=True)

def create_proof_path(i):
    """Return folder path for proof #i."""
    p = os.path.join(PROOFS_DIR, str(i))
    os.makedirs(p, exist_ok=True)
    return p

def run_command(cmd):
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        raise Exception("Command failed")
    return result.stdout

def generate_random_merkle_input():
    # 32 bytes = 64 hex chars
    leaf = "0x" + secrets.token_hex(32)
    pathElements = ["0x" + secrets.token_hex(32) for _ in range(50)]
    pathIndices = [random.randint(0, 1) for _ in range(50)]  # integer 0 or 1

    return {"leaf": leaf, "pathElements": pathElements, "pathIndices": pathIndices}

def create_proof(i):
    dst = create_proof_path(i)
    proof_json = os.path.join(dst, "proof.json")
    public_json = os.path.join(dst, "public.json")
    inp = {"x": str(1000+i)}
    # inp = generate_random_merkle_input()
    inp_path = os.path.join(BUILD_DIR, "input.json")
    with open(inp_path, "w") as f:
        json.dump(inp, f)
    run_command(
        [
            "node",
            os.path.join(BUILD_DIR, f"{CIRCUIT_NAME}_js", "generate_witness.js"),
            os.path.join(BUILD_DIR, f"{CIRCUIT_NAME}_js", f"{CIRCUIT_NAME}.wasm"),
            inp_path,
            os.path.join(BUILD_DIR, "witness.wtns"),
        ]
    )

    run_command(
        [
            "snarkjs",
            "groth16",
            "prove",
            os.path.join(BUILD_DIR, f"{CIRCUIT_NAME}.zkey"),
            os.path.join(BUILD_DIR, "witness.wtns"),
            proof_json,
            public_json,
        ]
    )

def main():
    N=5000
    for i in range(6000,6000+N):
        print(f"🔧 Generating proof #{i}")
        create_proof(i)
        
main()