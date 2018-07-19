#pragma once

#include <eosiolib/currency.hpp>
#include <eosiolib/vector.hpp>
#include <eosiolib/eosio.hpp>

#include <string>

class airdrop : public eosio::contract {
private:
	struct drop {
		eosio::symbol_type symbol;
		account_name user;
        uint64_t primary_key() const { return symbol.name(); }
	};

	typedef eosio::multi_index<N(drop), drop> drop_index;

public:
	airdrop(account_name self) :
		eosio::contract(self)
	{}

	void create(account_name issuer, account_name token_contract, eosio::asset asset);
	void drop(account_name token_contract, eosio::asset asset, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts);
	void withdraw(account_name token_contract, eosio::asset value);
};
