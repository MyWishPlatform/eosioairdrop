extern "C" {
	void apply(uint64_t receiver, uint64_t code, uint64_t action) {
		airdrop thiscontract(receiver);
		thiscontract.apply(code, action);
		eosio_exit(0);
	}
}

void airdrop::apply(account_name contract, uint64_t action) {
	if (action == N(transfer)) {
		struct transfer_t {
			account_name from;
			account_name to;
			eosio::asset quantity;
			std::string memo;
		} data = eosio::unpack_action_data<transfer_t>();
		if (data.from != this->_self) {
			this->on_deposit(std::stoi(data.memo), eosio::extended_asset(data.quantity, contract));
		}
	}
	if (contract == this->_self) {
		switch (action) {
			case N(create): {
				struct create_t {
					uint64_t pk;
					account_name issuer;
					account_name token_contract;
					eosio::symbol_type symbol;
					uint64_t drops;
				} data = eosio::unpack_action_data<create_t>();
				this->create(data.pk, data.issuer, data.token_contract, data.symbol, data.drops);
				break;
			}
			case N(drop): {
				struct drop_t {
					uint64_t pk;
					eosio::vector<account_name> addresses;
					eosio::vector<int64_t> amounts;
				} data = eosio::unpack_action_data<drop_t>();
				this->drop(data.pk, data.addresses, data.amounts);
				break;
			}
			case N(withdraw): {
				struct withdraw_t {
					uint64_t pk;
					eosio::asset value;
				} data = eosio::unpack_action_data<withdraw_t>();
				this->withdraw(data.pk, data.value);
				break;
			}
			default: {
				eosio_assert(false, "No such method");
				break;
			}
		}
	}
}
