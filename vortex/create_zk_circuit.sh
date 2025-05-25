#!/usr/bin/env bash
set -e

BUILD_DIR="build"
mkdir -p "${BUILD_DIR}"

# ─── Configuration ───────────────────────────────────────────────────────────
CIRCUIT="zk_circuit_1"
PTAU_PREFIX="pot15"
BUILD_DIR="build"
CIRCUIT_PATH="circuits/${CIRCUIT}.circom"

# ─── 1) Compile the circuit ─────────────────────────────────────────────────
echo "📐 Compiling ${CIRCUIT_PATH}..."
circom ${CIRCUIT_PATH} \
  --r1cs --wasm --sym \
  -o ${BUILD_DIR}/ \
  -l node_modules/

# ─── 2) Phase-1: Powers of Tau ───────────────────────────────────────────────
echo "🔑 Phase-1: Powers of Tau..."
snarkjs powersoftau new bn128 15 \
  ${BUILD_DIR}/${PTAU_PREFIX}_0000.ptau -v

snarkjs powersoftau contribute \
  ${BUILD_DIR}/${PTAU_PREFIX}_0000.ptau \
  ${BUILD_DIR}/${PTAU_PREFIX}_0001.ptau \
  --name="DebRC" -v

snarkjs powersoftau prepare phase2 \
  ${BUILD_DIR}/${PTAU_PREFIX}_0001.ptau \
  ${BUILD_DIR}/${PTAU_PREFIX}_final.ptau -v

# ─── 3) Phase-2: Groth16 setup ────────────────────────────────────────────────
echo "🔧 Phase-2: Circuit-specific Groth16 setup..."
snarkjs groth16 setup \
  ${BUILD_DIR}/${CIRCUIT}.r1cs \
  ${BUILD_DIR}/${PTAU_PREFIX}_final.ptau \
  ${BUILD_DIR}/${CIRCUIT}_0000.zkey

snarkjs zkey contribute \
  ${BUILD_DIR}/${CIRCUIT}_0000.zkey \
  ${BUILD_DIR}/${CIRCUIT}.zkey \
  --name="DebRC" -v

# ─── 4) Export Verification Key ───────────────────────────────────────────────
echo "🔑 Exporting verification key..."
snarkjs zkey export verificationkey \
  ${BUILD_DIR}/${CIRCUIT}.zkey \
  ${BUILD_DIR}/verification_key.json

# ─── 5) Generate Solidity Verifier ───────────────────────────────────────────
echo "📜 Generating Verifier.sol..."
snarkjs zkey export solidityverifier \
  ${BUILD_DIR}/${CIRCUIT}.zkey \
  contracts/Verifier.sol

echo "✅ Done! Artifacts in ${BUILD_DIR}/:"
ls -1 ${BUILD_DIR}/${CIRCUIT}.* ${BUILD_DIR}/${PTAU_PREFIX}_* ${BUILD_DIR}/verification_key.json