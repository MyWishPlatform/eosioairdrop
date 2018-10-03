#pragma once

#include <eosiolib/currency.hpp>
#include <eosiolib/vector.hpp>
#include <eosiolib/eosio.hpp>

#define PK(contract, symbol) ((static_cast<uint128_t>(contract) << 64) + (symbol.value))

class airdrop : public eosio::contract {
private:
	struct transfer_t {
		account_name from;
		account_name to;
		eosio::asset quantity;
		std::string memo;
	};

	struct drop {
		uint64_t pk;
		eosio::extended_asset available;

		uint64_t primary_key() const { return pk; }
		uint128_t get_contract_symbol() const { return PK(this->available.contract, this->available.symbol); }
	};

	struct drops {
		account_name user;
		bool sent;
	};

	typedef eosio::multi_index<N(drop), drop, eosio::indexed_by<N(contractsymb), eosio::const_mem_fun<drop, uint128_t, &drop::get_contract_symbol>>> drop_index;
	typedef eosio::multi_index<N(drops), drops> drops_index;

	void on_deposit(account_name issuer, eosio::extended_asset value);

public:
	airdrop(account_name self) :
		eosio::contract(self)
	{}

	void create(account_name issuer, account_name token_contract, eosio::symbol_type symbol);
	void drop(account_name issuer, account_name token_contract, eosio::symbol_type symbol, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts);
	void withdraw(account_name issuer, account_name token_contract, eosio::asset value);
	void apply(account_name contract, uint64_t action);
};
