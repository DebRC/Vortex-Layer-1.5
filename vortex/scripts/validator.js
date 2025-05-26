require('dotenv').config();
const fs = require('fs');
const path = require('path');
const {
  JsonRpcProvider,
  Wallet,
  Contract,
  keccak256,
  AbiCoder,
  parseUnits
} = require('ethers');
const { execFile } = require('child_process');
const { promisify } = require('util');
const { error } = require('console');

const RPC_URL = process.env.RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY_2;
const VORTEX_ADDRESS = process.env.VORTEX_CONTRACT_ADDRESS;
const VORTEX_ABI = require("../artifacts/contracts/VortexStorage.sol/VortexStorage.json").abi;
const VERIFICATION_KEY  = path.resolve(__dirname, "../build/verification_key.json");

const FETCH_INTERVAL = 2000;  // ms
const VERIFY_INTERVAL = 2000;  // ms
const SUBMIT_INTERVAL = 2000;  // ms
const DELAY_BLOCKS = 3;     // blocks to wait before submit

const proofs = new Map();

const provider = new JsonRpcProvider(RPC_URL);
const wallet = new Wallet(PRIVATE_KEY, provider);
const vortex = new Contract(VORTEX_ADDRESS, VORTEX_ABI, wallet);
const abiCoder = new AbiCoder();
const execAsync = promisify(execFile);

async function fetchProofs() {
  try {
    const topic = vortex.interface.getEvent("ProofAnnounced").topic;
    const logs = await provider.getLogs({
      fromBlock: 'latest',
      toBlock: 'latest',
      address: vortex.address,
      topics: [topic]
    });
    const currentBlock = await provider.getBlockNumber();
    for (const log of logs) {
      const { proofId, a, b, c, publicInputs } = vortex.interface.parseLog(log).args;
      const key = proofId.toString();
      if (proofs.has(key)) continue;
      console.log(`[FETCH] Fetched Proof ${key} :: Block ${currentBlock}`);
      proofs.set(key, {
        status: "pending",
        blockNumber: log.blockNumber,
        a: a.map(x => x.toString()),
        b: b.map(r => r.map(x => x.toString())),
        c: c.map(x => x.toString()),
        publicInputs: publicInputs.map(x => x.toString())
      });
    }
  }
  catch (err) {
    console.error("[FETCH] Proof Fetch Error ::", err.message);
  }
}

async function verifyProofs() {
  const batch = Array.from(proofs.entries())
    .filter(([_, p]) => p.status === "pending");
  
  await Promise.all(batch.map(async ([key,p]) => {
    p.status = "verifying";  // lock immediately
    const tmp = path.join(__dirname, "../cache/verify", key);
    fs.mkdirSync(tmp, { recursive: true });
    fs.writeFileSync(path.join(tmp,"proof.json"),  JSON.stringify({ pi_a:p.a, pi_b:p.b, pi_c:p.c },null,2));
    fs.writeFileSync(path.join(tmp,"public.json"), JSON.stringify(p.publicInputs,null,2));
    try {
      const { stdout, stderr } = await execAsync(
        "snarkjs",
        ["groth16","verify", VERIFICATION_KEY, path.join(tmp,"public.json"), path.join(tmp,"proof.json")],
        { cwd: __dirname }
      );
      process.stdout.write(stdout);
      if (stdout.includes("OK!")) {
        console.log(`[VERIFY] Proof ${key} OK`);
        p.status = "verified";
      } else {
        throw error;
      }
    } catch (err) {
      console.error(`[VERIFY] Proof ${key} FAIL`, err.stderr||err.message);
      p.status = "failed";
    }
  }));
}

async function submitProofs() {
  const currentBlock = await provider.getBlockNumber();
  const batch = Array.from(proofs.entries())
    .filter(([key,p]) => {
      if (p.status !== "verified" || p.status === "failed") return false;
      if (p.statusLock) return false; // skip if in-flight
      // check delay window
      if (currentBlock >= p.blockNumber + DELAY_BLOCKS){
        console.log(`[Expired] Proof ${key} cannot be Submitted`);
        p.status = "failed";
        return false;
      }
      return currentBlock >= p.blockNumber + DELAY_BLOCKS - 1
          && currentBlock <= p.blockNumber + DELAY_BLOCKS;
    });

  if (batch.length === 0) return;

  const baseNonce = await provider.getTransactionCount(wallet.address, 'pending');
  const to        = VORTEX_ADDRESS;
  const from      = wallet.address;

  await Promise.all(batch.map(async ([key,p], idx) => {
    p.status = "submitting"; // lock
    const proofId = key;

    const blob  = abiCoder.encode(
      ['uint256[2]','uint256[2][2]','uint256[2]','uint256[]'],
      [ p.a, p.b, p.c, p.publicInputs.map(x => x.toString()) ]
    );
    const state = keccak256(blob);
    const data  = vortex.interface.encodeFunctionData("submitState",[proofId, state]);

    let gasEstimate;
    try {
      gasEstimate = await provider.estimateGas({ to, from, data, nonce: baseNonce + idx });
      console.log(`[ESTIMATE] Proof ${key} Gas :: ${gasEstimate}`);
    } catch {
      gasEstimate = 500_000;
      console.log(`[ESTIMATE] Proof ${key} Error Estimation. Default Gas :: ${gasEstimate}`);
    }
    const baseFee = parseUnits("10", "gwei");
    const priority = parseUnits("2", "gwei");
    const maxFee = BigInt(baseFee) + BigInt(priority);

    try {
      const tx = await vortex.submitState(key, state, {
        from: from,
        nonce: baseNonce + idx,
        gasLimit: gasEstimate,
        maxFeePerGas: maxFee,
        maxPriorityFeePerGas: priority
      });
      console.log(`[SUBMIT] Proof ${key} Submitted :: 0x${tx.hash}, Nonce :: ${tx.nonce}`);
      const rc = await tx.wait(1);
      console.log(`[CONFIRM] Proof ${key} Confirmed :: Block ${rc.blockNumber}`);
      p.status = "submitted";
    } catch (err) {
      console.error(`[SUBMIT] Proof ${key} FAIL`, err.message);
    }
  }));
}

// ─── Kick off loops ───────────────────────────────────────
console.log("vortex_worker starting…");
setInterval(fetchProofs, FETCH_INTERVAL);
setInterval(verifyProofs, VERIFY_INTERVAL);
setInterval(submitProofs, SUBMIT_INTERVAL);