#[starknet::contract]
mod TestContract {
    #[storage]
    struct Storage {
        value: felt252,
    }

    #[constructor]
    fn constructor(ref self: ContractState, initial_value: felt252) {
        self.value.write(initial_value);
    }

    #[external(v0)]
    fn get_value(self: @ContractState) -> felt252 {
        self.value.read()
    }
}
