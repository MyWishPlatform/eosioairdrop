#pragma once

#include <eosiolib/currency.hpp>
#include <eosiolib/vector.hpp>
#include <eosiolib/eosio.hpp>

#define PK(contract, symbol) ((static_cast<uint128_t>(contract) << 64) + (symbol.value))

class airdrop : public eosio::contract {
private:
	struct drop {
		uint64_t pk;
		account_name contract;
		eosio::symbol_type symbol;

		uint64_t primary_key() const { return pk; }
		uint128_t get_contract_symbol() const { return PK(this->contract, this->symbol); }

		EOSLIB_SERIALIZE(drop, (pk)(contract)(symbol))
	};

	typedef eosio::multi_index<N(drop), drop, eosio::indexed_by<N(contractsymb), eosio::const_mem_fun<drop, uint128_t, &drop::get_contract_symbol>>> drop_index;

public:
	airdrop(account_name self) :
		eosio::contract(self)
	{}

	void create(account_name issuer, account_name token_contract, eosio::symbol_type symbol);
	void drop(account_name issuer, account_name token_contract, eosio::symbol_type symbol, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts);
	void withdraw(account_name issuer, account_name token_contract, eosio::asset value);
};
