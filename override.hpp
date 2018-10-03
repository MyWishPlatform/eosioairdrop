extern "C" {
	void apply(uint64_t receiver, uint64_t code, uint64_t action) {
		airdrop thiscontract(receiver);
		thiscontract.apply(code, action);
		eosio_exit(0);
	}
}

void airdrop::apply(account_name contract, uint64_t action) {
	if (action == N(transfer)) {
		transfer_t data = eosio::unpack_action_data<transfer_t>();
		this->on_deposit(data.from, eosio::extended_asset(data.quantity, contract));
	}
	if (contract == this->_self) {
		switch (action) {
			case N(create): {
				struct create_t {
					account_name issuer;
					account_name token_contract;
					eosio::symbol_type symbol;
				} data = eosio::unpack_action_data<create_t>();
				this->create(data.issuer, data.token_contract, data.symbol);
				break;
			}
			default: {
				eosio_assert(false, "No such method");
			}
		}
	}
}
