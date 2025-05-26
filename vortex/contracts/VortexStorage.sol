// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VortexStorage {
    uint256 public nextProofId;

    /// @notice Announce a zk-SNARK proof (Groth16) in compact typed form
    event ProofAnnounced(
        uint256 indexed proofId,
        address indexed submitter,
        uint256[2] a,
        uint256[2][2] b,
        uint256[2] c,
        uint256[] publicInputs
    );

    /// @notice Submit the computed state (e.g. a hash of the proof data)
    event StateSubmitted(uint256 indexed proofId, bytes32 state);

    /// @notice Announce a proof — cheapest calldata (∼200 bytes)
    function announceProof(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        uint256[] calldata publicInputs
    ) external {
        emit ProofAnnounced(nextProofId, msg.sender, a, b, c, publicInputs);
        nextProofId++;
    }

    /// @notice After off-chain verification, emit state
    function submitState(uint256 proofId, bytes32 state) external {
        emit StateSubmitted(proofId, state);
    }
}
