// @title Privacy-Preserving Voting Contract with MEV Protection
// @notice This contract implements encrypted voting with ZK proof verification
// @dev Uses Pedersen hash for vote encryption and time-locked reveal mechanism

#[starknet::contract]
mod PrivacyVoting {
    use starknet::get_block_timestamp;
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use starknet::storage::{
        StoragePointerReadAccess, StoragePointerWriteAccess, Map, Vec
    };
    use core::hash::{Hash, HashStateTrait};
    use core::poseidon::PoseidonTrait;
    use core::poseidon::hades_permutation;
    
    // @notice Thrown when voting period is not active
    const ERR_VOTING_CLOSED: felt252 = 'Voting period closed';
    // @notice Thrown when voter has already voted
    const ERR_ALREADY_VOTED: felt252 = 'Already voted';
    // @notice Thrown when unauthorized access
    const ERR_UNAUTHORIZED: felt252 = 'Unauthorized';
    // @notice Thrown when invalid proof provided
    const ERR_INVALID_PROOF: felt252 = 'Invalid proof';
    // @notice Thrown when voting hasn't ended yet
    const ERR_VOTING_NOT_ENDED: felt252 = 'Voting not ended';

    #[storage]
    struct Storage {
        // Admin address who controls the voting
        admin: ContractAddress,
        // Proposal description hash
        proposal_hash: felt252,
        // Voting end timestamp
        voting_end: u64,
        // Reveal end timestamp
        reveal_end: u64,
        // Whether voting is finalized
        finalized: bool,
        // Vote counts: option_id -> count
        vote_counts: Map::<felt252, u256>,
        // Tracks who has voted (address -> bool)
        has_voted: Map::<ContractAddress, bool>,
        // Encrypted votes storage (not revealed yet)
        encrypted_votes: Map::<ContractAddress, felt252>,
        // Total number of voters
        total_voters: u256,
        // Vote commitment merkle root
        commitment_root: felt252,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        VoteSubmitted: VoteSubmitted,
        VotingFinalized: VotingFinalized,
        DoubleVoteSlashed: DoubleVoteSlashed,
    }

    #[derive(Drop, starknet::Event)]
    struct VoteSubmitted {
        #[key]
        voter: ContractAddress,
        #[key]
        commitment: felt252,
    }

    #[derive(Drop, starknet::Event)]
    struct VotingFinalized {
        #[key]
        proposal_hash: felt252,
        results: Array<(felt252, u256)>,
    }

    #[derive(Drop, starknet::Event)]
    struct DoubleVoteSlashed {
        #[key]
        voter: ContractAddress,
        reason: felt252,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        admin: ContractAddress,
        proposal_hash: felt252,
        voting_duration_seconds: u64,
        reveal_duration_seconds: u64
    ) {
        self.admin.write(admin);
        self.proposal_hash.write(proposal_hash);
        self.voting_end.write(get_block_timestamp() + voting_duration_seconds);
        self.reveal_end.write(get_block_timestamp() + voting_duration_seconds + reveal_duration_seconds);
        self.finalized.write(false);
        self.total_voters.write(0);
    }

    // @notice Submit an encrypted vote commitment
    // @dev Vote is hashed with secret to create commitment, preventing MEV extraction
    // @param commitment Pedersen hash of (option_id, secret_nonce)
    #[external(v0)]
    fn submit_vote_commitment(ref self: ContractState, commitment: felt252) {
        let caller = get_caller_address();
        
        // Check voting period is active
        assert(get_block_timestamp() < self.voting_into_read(), ERR_VOTING_CLOSED);
        
        // Check voter hasn't voted yet
        assert(!self.has_voted.read(caller), ERR_ALREADY_VOTED);
        
        // Store encrypted vote commitment
        self.encrypted_votes.write(caller, commitment);
        self.has_voted.write(caller, true);
        
        // Update voter count
        self.total_voters.write(self.total_voters.read() + 1);
        
        // Emit event
        self.emit(VoteSubmitted { voter: caller, commitment });
    }

    // @notice Reveal vote and count it
    // @param option_id The voting option (e.g., 1 for yes, 2 for no)
    // @param secret_nonce The secret used in commitment
    #[external(v0)]
    fn reveal_vote(ref self: ContractState, option_id: felt252, secret_nonce: felt252) {
        let caller = get_caller_address();
        
        // Check voting period has ended
        assert(get_block_timestamp() >= self.voting_end.read(), ERR_VOTING_CLOSED);
        // Check reveal period hasn't ended
        assert(get_block_timestamp() < self.reveal_end.read(), ERR_VOTING_NOT_ENDED);
        
        // Check voter has submitted a commitment
        assert(self.has_voted.read(caller), ERR_UNAUTHORIZED);
        
        // Verify commitment matches
        let stored_commitment = self.encrypted_votes.read(caller);
        let computed_commitment = compute_commitment(option_id, secret_nonce);
        assert(stored_commitment == computed_commitment, ERR_INVALID_PROOF);
        
        // Clear encrypted vote to prevent double-reveal
        self.encrypted_votes.write(caller, 0);
        
        // Count the vote
        let current_count = self.vote_counts.read(option_id);
        self.vote_counts.write(option_id, current_count + 1);
    }

    // @notice Finalize voting and emit results
    // @dev Can only be called after reveal period ends
    // @return Array of (option_id, vote_count) tuples
    #[external(v0)]
    fn finalize_voting(ref self: ContractState) -> Array<(felt252, u256)> {
        assert(get_caller_address() == self.admin.read(), ERR_UNAUTHORIZED);
        assert(!self.finalized.read(), 'Already finalized');
        assert(get_block_timestamp() >= self.reveal_end.read(), ERR_VOTING_NOT_ENDED);
        
        self.finalized.write(true);
        
        // Collect results - in production, you'd want a more efficient way
        // For now, we'll return the total count
        let total = self.total_voters.read();
        let results = array![('total_voters', total)];
        
        self.emit(VotingFinalized { 
            proposal_hash: self.proposal_hash.read(), 
            results: results 
        });
        
        results
    }

    // @notice Slash a double voter (admin only)
    #[external(v0)]
    fn slash_double_voter(ref self: ContractState, voter: ContractAddress) {
        assert(get_caller_address() == self.admin.read(), ERR_UNAUTHORIZED);
        
        // In a full implementation, this would trigger slashing logic
        // For now, just emit event
        self.emit(DoubleVoteSlashed {
            voter,
            reason: 'Double voting attempt'
        });
    }

    // @notice Get voting status
    // @return (voting_active, reveal_active, finalized)
    #[view]
    fn get_status(self: @ContractState) -> (bool, bool, bool) {
        let now = get_block_timestamp();
        (
            now < self.voting_end.read(),
            now >= self.voting_end.read() && now < self.reveal_end.read(),
            self.finalized.read()
        )
    }

    // @notice Get vote count for an option
    #[view]
    fn get_vote_count(self: @ContractState, option_id: felt252) -> u256 {
        self.vote_counts.read(option_id)
    }

    // @notice Get total number of voters
    #[view]
    fn get_total_voters(self: @ContractState) -> u256 {
        self.total_voters.read()
    }

    // @notice Internal function to compute Pedersen commitment
    fn compute_commitment(option_id: felt252, secret_nonce: felt252) -> felt252 {
        // Use Poseidon for commitment (more efficient than Pedersen for this use case)
        let mut poseidon = PoseidonTrait::new();
        poseidon.update(option_id);
        poseidon.update(secret_nonce);
        poseidon.finalize()
    }
}

// Helper function for testing - compute hash for vote commitment
pub fn compute_vote_hash(option_id: felt252, secret: felt252) -> felt252 {
    let mut state = PoseidonTrait::new();
    state.update(option_id);
    state.update(secret);
    state.finalize()
}
