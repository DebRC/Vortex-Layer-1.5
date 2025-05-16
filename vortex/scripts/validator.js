// require('dotenv').config();
// const { JsonRpcProvider, Wallet, Contract, toUtf8Bytes, hexlify } = require("ethers");

// const ABI = require("../artifacts/contracts/VortexStorage.sol/VortexStorage.json").abi;

// const provider = new JsonRpcProvider(process.env.RPC_URL);
// const wallet = new Wallet(process.env.PRIVATE_KEY, provider);
// const contract = new Contract(process.env.CONTRACT_ADDRESS, ABI, wallet);

// let currentNonce = null;
// const delay = 3;

// function verifyProof(data) {
//     return data.length > 0;
// }

// function computeState(proofId) {
//     return hexlify(toUtf8Bytes(`state-for-${proofId}`));
// }

// async function loop() {
//     try {
//         const pendingIds = await contract.getPendingStateProofs();
//         console.log(`🔄 Pending proofs: [${pendingIds.join(", ")}]`);

//         if (currentNonce === null) {
//             currentNonce = await provider.getTransactionCount(wallet.address, "pending");
//         }

//         const currentBlock = await provider.getBlockNumber();

//         for (const proofId of pendingIds) {
//             const [, blockNumber, , data] = await contract.getProof(proofId);
//             const blockNum = Number(blockNumber);

//             console.log(`🔍 Verifying proof ${proofId}...`);

//             if (!verifyProof(data)) {
//                 console.log(`⛔ Proof ${proofId} failed verification.`);
//                 continue;
//             }

//             console.log(`✅ Proof ${proofId} verified successfully.`);
//             console.log(`⏳ Waiting for ${delay} blocks before submitting...`);

//             if (currentBlock < blockNum + delay - 1) {
//                 continue; // wait at least delay-1 blocks
//             }

//             if (currentBlock > blockNum + delay) {
//                 console.log(`⚠️  Proof ${proofId} expired (submitted too long ago). Skipping.`);
//                 continue;
//             }

//             const state = computeState(proofId);
//             console.log(`📦 Submitting state for proof ${proofId} with nonce ${currentNonce}`);

//             try {
//                 const tx = await contract.submitState(proofId, state, {
//                     nonce: currentNonce
//                 });
//                 console.log(`✅ State submitted for proof ${proofId}`);
//                 currentNonce++;
//             } catch (err) {
//                 console.error(`❌ Failed to submit proof ${proofId}: ${err.message}`);
//             }
//         }
//     } catch (err) {
//         console.error("🔴 Error in validator loop:", err.message || err);
//     }
// }

// setInterval(loop, 12000);

require('dotenv').config();
const { JsonRpcProvider, Wallet, Contract } = require("ethers");
const { execSync } = require("child_process");

const ABI = require("../artifacts/contracts/VortexStorage.sol/VortexStorage.json").abi;

const provider = new JsonRpcProvider(process.env.RPC_URL);
const wallet = new Wallet(process.env.PRIVATE_KEY, provider);
const contract = new Contract(process.env.VORTEX_CONTRACT_ADDRESS, ABI, wallet);

let currentNonce = null;
const delay = 3;

function verifyProofWithPython(proofData) {
    const fs = require('fs');
    const path = require('path');
    const proofPath = path.join(__dirname, '../build/proof.json');
    fs.writeFileSync(proofPath, JSON.stringify(proofData));
    try {
        const output = execSync("python3 scripts/verify_proof.py", { encoding: "utf-8" });
        return output.includes("✅ Proof verified successfully.");
    } catch (error) {
        console.error("Proof verification failed:", error);
        return false;
    }
}

async function loop() {
    try {
        const pendingIds = await contract.getPendingStateProofs();
        console.log(`🔄 Pending proofs: [${pendingIds.join(", ")}]`);

        if (currentNonce === null) {
            currentNonce = await provider.getTransactionCount(wallet.address, "pending");
        }

        const currentBlock = await provider.getBlockNumber();

        for (const proofId of pendingIds) {
            const [, blockNumber, , data] = await contract.getProof(proofId);
            const blockNum = Number(blockNumber);

            console.log(`🔍 Verifying proof ${proofId}...`);

            const proofData = JSON.parse(data.toString());

            if (!verifyProofWithPython(proofData)) {
                console.log(`⛔ Proof ${proofId} failed verification.`);
                continue;
            }

            console.log(`✅ Proof ${proofId} verified successfully.`);
            console.log(`⏳ Waiting for ${delay} blocks before submitting...`);

            if (currentBlock < blockNum + delay - 1) {
                continue; // wait at least delay-1 blocks
            }

            if (currentBlock > blockNum + delay) {
                console.log(`⚠️  Proof ${proofId} expired. Skipping.`);
                continue;
            }
            const state = JSON.stringify({ state: `state-for-${proofId}` });
            console.log(`📦 Submitting state for proof ${proofId} with nonce ${currentNonce}`);
            try {
                const tx = await contract.submitState(proofId, state, {
                    nonce: currentNonce
                });
                console.log(`✅ State submitted for proof ${proofId}`);
                currentNonce++;
            } catch (err) {
                console.error(`❌ Failed to submit proof ${proofId}: ${err.message}`);
            }
        }
    }
    catch (err) {
        console.error("🔴 Error in validator loop:", err.message || err);
    }
}
setInterval(loop, 12000);