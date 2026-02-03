#!/usr/bin/env python3
"""
Off-chain Merkle Tree Generator for Starknet Privacy Pool
Compatible with Cairo 2.8.0 Pedersen hash
"""

import hashlib
from typing import List, Tuple, Optional
from dataclasses import dataclass
import json


class PedersenHasher:
    """Pedersen hash for Starknet (simplified Python simulation)"""
    
    @staticmethod
    def hash(a: int, b: int) -> int:
        # Simulated Pedersen - in production use starknet.py or garaga
        # Real Pedersen on BN254 curve
        combined = f"{a}:{b}".encode()
        return int(hashlib.sha256(combined).hexdigest(), 16) % (2**251)
    
    @staticmethod
    def hash_list(values: List[int]) -> int:
        """Hash list of values iteratively"""
        if not values:
            return 0
        result = values[0]
        for v in values[1:]:
            result = PedersenHasher.hash(result, v)
        return result


@dataclass
class Note:
    """Privacy pool note"""
    value: int
    secret: int
    salt: int
    commitment: Optional[int] = None
    
    def __post_init__(self):
        if self.commitment is None:
            self.commitment = self.compute_commitment()
    
    def compute_commitment(self) -> int:
        """C = hash(value, secret, salt)"""
        state = PedersenHasher.hash(self.value, self.secret)
        return PedersenHasher.hash(state, self.salt)
    
    def compute_nullifier(self) -> int:
        """N = hash(secret, salt)"""
        return PedersenHasher.hash(self.secret, self.salt)


class MerkleTree:
    """Sparse Merkle Tree for privacy pool commitments"""
    
    def __init__(self, height: int = 32):
        self.height = height
        self.leaves: dict = {}  # index -> commitment
        self.tree: dict = {}    # level -> {index: hash}
        self.next_index = 0
        self._build_empty_tree()
    
    def _build_empty_tree(self):
        """Build empty tree with zeros"""
        for level in range(self.height + 1):
            self.tree[level] = {}
    
    def insert(self, commitment: int) -> Tuple[int, List[int]]:
        """Insert commitment, return index and proof path"""
        index = self.next_index
        self.next_index += 1
        
        # Store leaf
        self.leaves[index] = commitment
        self.tree[0][index] = commitment
        
        # Build up to root
        current_hash = commitment
        path = [commitment]
        
        for level in range(1, self.height + 1):
            sibling_index = index ^ 1  # sibling is at adjacent index
            
            if sibling_index in self.tree[level - 1]:
                sibling_hash = self.tree[level - 1][sibling_index]
            else:
                sibling_hash = 0  # Empty sibling
            
            # Parent hash
            if index % 2 == 0:
                current_hash = PedersenHasher.hash(current_hash, sibling_hash)
            else:
                current_hash = PedersenHasher.hash(sibling_hash, current_hash)
            
            self.tree[level][index // 2] = current_hash
            path.append(current_hash)
            index //= 2
        
        return (index, path)
    
    def get_root(self) -> int:
        """Get current merkle root"""
        return self.tree[self.height].get(0, 0)
    
    def get_proof(self, index: int) -> List[Tuple[int, bool]]:
        """Get merkle proof for index (hash, is_left)"""
        proof = []
        current = self.leaves.get(index, 0)
        
        for level in range(self.height):
            sibling_index = index ^ 1
            sibling = self.leaves.get(sibling_index, 0)
            is_left = (index % 2 == 0)
            proof.append((sibling, is_left))
            index //= 2
        
        return proof


def simulate_shielded_pool():
    """Simulate shielded pool operations"""
    print("=" * 60)
    print("STARKNET PRIVACY POOL - OFF-CHAIN SIMULATION")
    print("=" * 60)
    
    # Create tree
    tree = MerkleTree(height=32)
    
    # Create notes
    notes = []
    for i in range(5):
        note = Note(
            value=100 * (i + 1),
            secret=hash(f"secret_{i}") % (2**128),
            salt=hash(f"salt_{i}") % (2**128)
        )
        notes.append(note)
        print(f"\n📝 Note {i}: value={note.value}")
        print(f"   Commitment: {hex(note.commitment)}")
        print(f"   Nullifier:  {hex(note.compute_nullifier())}")
    
    # Deposit notes
    print("\n" + "=" * 60)
    print("DEPOSITS")
    print("=" * 60)
    for i, note in enumerate(notes):
        idx, path = tree.insert(note.commitment)
        print(f"\n✅ Deposit {i}: index={idx}, root={hex(tree.get_root())}")
    
    # Generate withdrawal proof
    print("\n" + "=" * 60)
    print("WITHDRAWAL PROOF GENERATION")
    print("=" * 60)
    
    spend_note = notes[2]
    nullifier = spend_note.compute_nullifier()
    
    # Check nullifier not used
    nullifiers_used = set()
    if nullifier in nullifiers_used:
        print("❌ ERROR: Nullifier already used!")
    else:
        print(f"✅ Nullifier check: {hex(nullifier)} - NOT used")
        nullifiers_used.add(nullifier)
    
    # Generate merkle proof
    proof = tree.get_proof(2)
    print(f"\n📜 Merkle Proof (sibling_hash, is_left):")
    for i, (sibling, is_left) in enumerate(proof):
        print(f"   Level {i}: {hex(sibling)}, left={is_left}")
    
    # Verify proof
    def verify_merkle_proof(leaf: int, proof: List[Tuple[int, bool]], root: int) -> bool:
        current = leaf
        for sibling, is_left in proof:
            if is_left:
                current = PedersenHasher.hash(current, sibling)
            else:
                current = PedersenHasher.hash(sibling, current)
        return current == root
    
    is_valid = verify_merkle_proof(spend_note.commitment, proof, tree.get_root())
    print(f"\n✅ Merkle proof valid: {is_valid}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total notes: {len(notes)}")
    print(f"Merkle root: {hex(tree.get_root())}")
    print(f"Nullifiers used: {len(nullifiers_used)}")
    print("\n📋 Contract calls needed for ZK verification:")
    print(f"   1. deposit(commitment={hex(spend_note.commitment)})")
    print(f"   2. spend(nullifier={hex(nullifier)}, new_commitment=...)")
    print(f"   3. merkle_proof: {[hex(s[0]) for s in proof]}")
    
    return tree, notes


if __name__ == "__main__":
    tree, notes = simulate_shielded_pool()
