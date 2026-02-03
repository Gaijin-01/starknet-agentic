// SPDX-License-Identifier: MIT
// Minimal ShieldedPool - Cairo 2.8.0 compatible (with deprecated_legacy_map)

#[starknet::contract]
#[feature("deprecated_legacy_map")]
mod ShieldedPoolMinimal {
    use starknet::ContractAddress;
    use starknet::get_caller_address;
    use core::hash::{HashStateTrait, Hash};
    use core::pedersen::PedersenTrait;

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // STORAGE - Using LegacyMap (deprecated but available in 2.8.0)
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    #[storage]
    struct Storage {
        // Core state
        merkle_root: felt252,
        next_index: u32,
        // Nullifier tracking (felt252 -> 0/1)
        nullifier_used: LegacyMap<felt252, felt252>,
        // Note storage (commitment -> 1 if valid)
        notes: LegacyMap<felt252, felt252>,
        // Admin
        owner: ContractAddress,
        // Pool state
        pool_balance: felt252,
    }

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        self.owner.write(owner);
        self.merkle_root.write(0);
        self.next_index.write(0);
        self.pool_balance.write(0);
    }

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // EXTERNAL: DEPOSIT
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    #[external(v0)]
    fn deposit(ref self: ContractState, commitment: felt252) -> u32 {
        assert(commitment != 0, 'Invalid commitment');
        
        // Store commitment
        let index = self.next_index.read();
        self.notes.write(commitment, 1);
        
        // Increment index
        self.next_index.write(index + 1);
        
        // TODO: Update merkle root (off-chain for now)
        
        index
    }

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // EXTERNAL: SPEND (Transfer/Withdraw)
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    #[external(v0)]
    fn spend(
        ref self: ContractState,
        nullifier: felt252,
        new_commitment: felt252,
    ) -> felt252 {
        // Check nullifier not used
        assert(self.nullifier_used.read(nullifier) == 0, 'Nullifier used');
        
        // Mark nullifier as used
        self.nullifier_used.write(nullifier, 1);
        
        // Store new commitment
        self.notes.write(new_commitment, 1);
        
        // TODO: ZK proof verification (when Garaga available)
        
        1 // Success
    }

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // EXTERNAL: ADMIN
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    #[external(v0)]
    fn set_merkle_root(ref self: ContractState, new_root: felt252) {
        assert(get_caller_address() == self.owner.read(), 'Not owner');
        self.merkle_root.write(new_root);
    }

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // EXTERNAL: VIEWS
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    #[external(v0)]
    fn is_nullifier_used(self: @ContractState, nullifier: felt252) -> felt252 {
        self.nullifier_used.read(nullifier)
    }

    #[external(v0)]
    fn get_merkle_root(self: @ContractState) -> felt252 {
        self.merkle_root.read()
    }

    #[external(v0)]
    fn get_next_index(self: @ContractState) -> u32 {
        self.next_index.read()
    }

    #[external(v0)]
    fn get_owner(self: @ContractState) -> ContractAddress {
        self.owner.read()
    }

    #[external(v0)]
    fn get_pool_balance(self: @ContractState) -> felt252 {
        self.pool_balance.read()
    }

    #[external(v0)]
    fn is_commitment_valid(self: @ContractState, commitment: felt252) -> felt252 {
        self.notes.read(commitment)
    }

    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    // INTERNAL: HASH HELPERS
    // ═══════════════════════════════════════════════════════════════════════════════════════════════
    fn hash_commitment(value: felt252, secret: felt252, salt: felt252) -> felt252 {
        let mut state = PedersenTrait::new(0);
        state = state.update(value);
        state = state.update(secret);
        state = state.update(salt);
        state.finalize()
    }

    fn hash_nullifier(secret: felt252, salt: felt252) -> felt252 {
        let mut state = PedersenTrait::new(0);
        state = state.update(secret);
        state = state.update(salt);
        state.finalize()
    }
}
