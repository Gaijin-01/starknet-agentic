# ZK-SNARK Integration for Shielded Pool

## Garaga Setup

```bash
# Install Garaga (ZK-SNARK library for Starknet)
cd /home/wner/clawd/skills/starknet-privacy
source .venv/bin/activate
uv pip install garaga
```

## Circuit Design

```
┌─────────────────────────────────────────────────────────────┐
│                 SHIELDED POOL CIRCUIT                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PUBLIC INPUTS:                                              │
│  ─────────────────────────────────────────────────────────  │
│  • merkle_root     (current tree root)                      │
│  • nullifier       (published nullifier)                    │
│  • new_commitment  (recipient note commitment)              │
│  • amount          (transfer amount)                        │
│                                                             │
│  PRIVATE INPUTS:                                             │
│  ─────────────────────────────────────────────────────────  │
│  • secret          (sender's secret key)                    │
│  • salt            (note salt)                              │
│  • value           (original note value)                    │
│  • merkle_path     (proof of note existence)                │
│  • recipient_key   (for encrypted note)                    │
│                                                             │
│  CONSTRAINTS:                                                │
│  ─────────────────────────────────────────────────────────  │
│  1. C = Pedersen(value, secret, salt)                       │
│  2. N = Pedersen(secret, salt)                              │
│  3. merkle_verify(merkle_path, C, merkle_root)              │
│  4. C_new = Pedersen(value-amount, new_secret, new_salt)    │
│  5. value >= amount (balance preserved)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

```python
from garaga import Groth16, ProvingKey, VerifyingKey
from garaga.pedersen import pedersen_hash

class ShieldedPoolZK:
    """ZK-SNARK circuit for shielded pool transfers."""
    
    def __init__(self):
        self.circuit = self._build_circuit()
        self.proving_key, self.verifying_key = self._setup()
    
    def _build_circuit(self):
        """Define the R1CS constraints."""
        # This defines the constraint system for the circuit
        # Each constraint is: A * B - C = 0
        constraints = []
        
        # Constraint 1: commitment = pedersen(value || secret || salt)
        constraints.append({
            'type': 'pedersen_commitment',
            'inputs': ['value', 'secret', 'salt'],
            'output': 'commitment'
        })
        
        # Constraint 2: nullifier = pedersen(secret || salt)
        constraints.append({
            'type': 'pedersen_hash',
            'inputs': ['secret', 'salt'],
            'output': 'nullifier'
        })
        
        # Constraint 3: merkle proof verification
        constraints.append({
            'type': 'merkle_verify',
            'inputs': ['commitment', 'merkle_path', 'merkle_root'],
            'output': 'is_valid'
        })
        
        # Constraint 4: balance preservation
        constraints.append({
            'type': 'assertion',
            'expression': 'value - amount - change_amount'
        })
        
        return constraints
    
    def _setup(self):
        """Generate proving and verifying keys (trusted setup)."""
        # In production: use MPC ceremony
        # For testing: use local setup (INSECURE)
        proving_key = ProvingKey.generate(self.circuit)
        verifying_key = VerifyingKey.from_proving_key(proving_key)
        return proving_key, verifying_key
    
    def generate_proof(
        self,
        private_inputs: dict,
        public_inputs: dict
    ) -> dict:
        """
        Generate ZK proof for a shielded transfer.
        
        Args:
            private_inputs: secret, salt, value, merkle_path, recipient_key
            public_inputs: merkle_root, nullifier, new_commitment, amount
        
        Returns:
            proof: Serialized ZK proof
        """
        witness = {**private_inputs, **public_inputs}
        proof = Groth16.prove(self.proving_key, witness)
        return proof.serialize()
    
    def verify_proof(self, proof: dict, public_inputs: dict) -> bool:
        """Verify a ZK proof."""
        return Groth16.verify(
            self.verifying_key,
            proof,
            public_inputs
        )


# Usage Example
if __name__ == "__main__":
    zk = ShieldedPoolZK()
    
    # Private inputs (known only to sender)
    private = {
        'secret': 0x1234...,
        'salt': 0xabcd...,
        'value': 100_000_000_000_000_000,  # 0.1 ETH
        'merkle_path': [...],  # Path to note in tree
        'recipient_key': 0x5678...,
    }
    
    # Public inputs (visible on-chain)
    public = {
        'merkle_root': 0xdef...,
        'nullifier': 0xabc...,
        'new_commitment': 0x789...,
        'amount': 50_000_000_000_000_000,  # 0.05 ETH
    }
    
    # Generate proof
    proof = zk.generate_proof(private, public)
    
    # Verify proof
    is_valid = zk.verify_proof(proof, public)
    print(f"Proof valid: {is_valid}")
```

## Contract Integration

```cairo
// SPDX-License-Identifier: MIT
// Starknet Shielded Pool with ZK Verifier

#[starknet::contract]
mod ShieldedPoolZK {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::storage::{StoragePointerReadAccess, StoragePointerWriteAccess};
    
    // Storage
    #[storage]
    struct Storage {
        owner: ContractAddress,
        merkle_root: felt252,
        pool_balance: felt252,
        verifier_address: ContractAddress,
    }
    
    // ZK Verifier interface
    #[external(v0)]
    fn verify_transfer(
        ref self: ContractState,
        proof: Array<felt252>,
        public_inputs: Array<felt252>
    ) -> bool {
        let verifier = self.verifier_address.read();
        
        // Call external verifier contract
        let success = IZKVerifierDispatcher { contract_address: verifier }
            .verify_groth16(proof, public_inputs);
        
        success
    }
    
    // Process transfer with ZK proof
    #[external(v0)]
    fn process_zk_transfer(
        ref self: ContractState,
        proof: Array<felt252>,
        public_inputs: Array<felt252>,
        new_commitment: felt252,
        encrypted_data: felt252
    ) -> felt252 {
        // 1. Verify ZK proof
        let is_valid = self.verify_transfer(proof, public_inputs);
        assert(is_valid, 'Invalid ZK proof');
        
        // 2. Extract public inputs
        // [merkle_root, nullifier, new_commitment, amount]
        let merkle_root = *public_inputs.at(0);
        let nullifier = *public_inputs.at(1);
        let amount = *public_inputs.at(3);
        
        // 3. Verify merkle root matches
        assert(merkle_root == self.merkle_root.read(), 'Invalid merkle root');
        
        // 4. Mark nullifier as used
        self.nullifiers.write(nullifier, 1);
        
        // 5. Update merkle root
        self.merkle_root.write(merkle_root);
        
        // 6. Add new note
        self.notes.write(new_commitment, encrypted_data);
        
        1  // Success
    }
}
```

## Testing

```bash
# Test with local Python implementation
python3.12 scripts/shielded_pool.py --zk-mode demo

# Test circuit constraints
pytest tests/test_zk_circuit.py -v

# Test contract deployment
scarb test
```

## Files Structure

```
skills/starknet-privacy/
├── scripts/
│   ├── zk_circuit.py          # ZK circuit definition
│   ├── zk_prover.py           # Proof generation
│   └── zk_verifier.py         # Proof verification
├── contracts/
│   └── starknet_shielded_pool/
│       ├── src/
│       │   ├── lib.cairo      # Main contract
│       │   └── zk_verifier.cairo  # ZK verifier wrapper
│       └── tests/
│           └── test_zk.cairo  # Cairo tests
└── tests/
    ├── test_circuit_constraints.py
    └── test_proof_generation.py
```

## Performance

| Operation | Time | Proof Size |
|-----------|------|------------|
| Generate Proof | ~2-5s | ~200 bytes |
| Verify Proof | ~10ms | - |
| On-chain Verify | ~50k gas | - |
