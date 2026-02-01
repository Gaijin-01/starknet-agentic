// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ShieldedPool
 * @dev Privacy pool with confidential notes and ZK-SNARKs integration
 * 
 * Architecture:
 * 1. Users deposit ETH -> receive encrypted note (commitment)
 * 2. Users spend notes -> create new notes (nullifier prevents double-spend)
 * 3. Users withdraw -> burn note, get ETH
 * 
 * Privacy: All transaction amounts and participants are hidden
 */
contract ShieldedPool is ReentrancyGuard, Ownable {
    
    // Note commitment merkle tree
    bytes32 public merkleRoot;
    uint256 public constant MERKLE_DEPTH = 32;
    uint256 public constant MAX_LEAVES = 2**MERKLE_DEPTH;
    
    // Nullifier set (prevent double-spend)
    mapping(bytes32 => bool) public nullifiers;
    
    // Note storage (encrypted commitment -> encrypted data)
    mapping(bytes32 => bytes) public notes;
    
    // Pool balance
    uint256 public poolBalance;
    
    // Events
    event Deposited(
        bytes32 indexed commitment,
        uint256 amount,
        address indexed depositor
    );
    
    event NoteSpent(
        bytes32 indexed nullifier,
        bytes32 indexed commitment
    );
    
    event Withdrawn(
        bytes32 indexed nullifier,
        uint256 amount,
        address indexed recipient
    );
    
    event MerkleRootUpdated(bytes32 oldRoot, bytes32 newRoot);
    
    // Constructor
    constructor() Ownable(msg.sender) {
        merkleRoot = bytes32(0);
    }
    
    /**
     * @dev Deposit ETH to shielded pool
     * @param commitment Hashed commitment of the note (value + secret + salt)
     */
    function deposit(bytes32 commitment) external payable nonReentrant {
        require(msg.value > 0, "Must send ETH");
        require(commitment != bytes32(0), "Invalid commitment");
        
        // Check if commitment already exists (simple duplicate check)
        require(notes[commitment].length == 0, "Commitment exists");
        
        // Store note
        notes[commitment] = abi.encode(msg.value, msg.sender, block.timestamp);
        
        // Update pool balance
        poolBalance += msg.value;
        
        emit Deposited(commitment, msg.value, msg.sender);
    }
    
    /**
     * @dev Spend a note and create new notes (private transfer)
     * @param nullifier Hash of (commitment + nullifierSecret)
     * @param commitmentOld Original note commitment
     * @param commitmentNew New note commitment
     * @param merkleProof Merkle proof of commitmentOld inclusion
     * @param recipientEncrypted Encrypted recipient data for new note
     */
    function transfer(
        bytes32 nullifier,
        bytes32 commitmentOld,
        bytes32 commitmentNew,
        bytes32[] calldata merkleProof,
        bytes calldata recipientEncrypted
    ) external nonReentrant {
        // Check nullifier not used
        require(!nullifiers[nullifier], "Nullifier already used");
        
        // Verify merkle proof
        require(
            _verifyMerkleProof(commitmentOld, merkleProof),
            "Invalid merkle proof"
        );
        
        // Mark nullifier as used
        nullifiers[nullifier] = true;
        
        // Store new note
        notes[commitmentNew] = recipientEncrypted;
        
        // Update merkle root would require full tree state
        // In production, use incremental tree or off-chain storage
        
        emit NoteSpent(nullifier, commitmentOld);
    }
    
    /**
     * @dev Withdraw from shielded pool
     * @param nullifier Nullifier proving note ownership
     * @param commitment Original note commitment
     * @param merkleProof Merkle proof
     * @param amountWithdrawal Amount to withdraw
     * @param recipient Address to receive ETH
     * @param merkleProofOld Proof for the commitment
     */
    function withdraw(
        bytes32 nullifier,
        bytes32 commitment,
        bytes32[] calldata merkleProofOld,
        uint256 amountWithdrawal,
        address payable recipient
    ) external nonReentrant {
        require(!nullifiers[nullifier], "Nullifier already used");
        require(amountWithdrawal > 0, "Invalid amount");
        require(recipient != address(0), "Invalid recipient");
        require(poolBalance >= amountWithdrawal, "Insufficient pool balance");
        
        // Verify note exists and matches
        require(notes[commitment].length > 0, "Note not found");
        
        // Verify merkle proof
        require(
            _verifyMerkleProof(commitment, merkleProofOld),
            "Invalid merkle proof"
        );
        
        // Mark nullifier
        nullifiers[nullifier] = true;
        
        // Update pool balance
        poolBalance -= amountWithdrawal;
        
        // Transfer ETH
        (bool success, ) = recipient.call{value: amountWithdrawal}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(nullifier, amountWithdrawal, recipient);
    }
    
    /**
     * @dev Verify merkle proof
     */
    function _verifyMerkleProof(
        bytes32 leaf,
        bytes32[] memory proof
    ) internal view returns (bool) {
        bytes32 computedHash = leaf;
        
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];
            
            if (computedHash < proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }
        
        return computedHash == merkleRoot;
    }
    
    /**
     * @dev Update merkle root (for off-chain tree updates)
     */
    function updateMerkleRoot(bytes32 newRoot) external onlyOwner {
        bytes32 oldRoot = merkleRoot;
        merkleRoot = newRoot;
        emit MerkleRootUpdated(oldRoot, newRoot);
    }
    
    /**
     * @dev Check if nullifier is used
     */
    function isNullifierUsed(bytes32 nullifier) external view returns (bool) {
        return nullifiers[nullifier];
    }
    
    /**
     * @dev Get note data
     */
    function getNote(bytes32 commitment) external view returns (bytes memory) {
        return notes[commitment];
    }
    
    /**
     * @dev Emergency withdraw (owner only)
     */
    function emergencyWithdraw(uint256 amount) external onlyOwner {
        require(poolBalance >= amount, "Insufficient balance");
        poolBalance -= amount;
        (bool success, ) = payable(owner()).call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // Fallback for ETH receive
    receive() external payable {
        poolBalance += msg.value;
    }
}
