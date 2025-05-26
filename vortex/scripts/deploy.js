const hre = require("hardhat");

async function main() {
  // Deploy Verifier contract
  const Verifier = await hre.ethers.getContractFactory("Groth16Verifier");
  const verifier = await Verifier.deploy();
  await verifier.waitForDeployment();
  const verifierAddress = await verifier.getAddress();
  console.log("Verifier deployed to:", verifierAddress);

  const VortexStorage = await hre.ethers.getContractFactory("VortexStorage");
  const vortex = await VortexStorage.deploy();
  await vortex.waitForDeployment();
  const vortexAddress = await vortex.getAddress();
  console.log("VortexStorage deployed to:", vortexAddress);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});