#pragma once

#include <eosiolib/currency.hpp>
#include <eosiolib/vector.hpp>
#include <eosiolib/eosio.hpp>

#define PK(ISSUER, TOKEN) ((static_cast<int128_t>(ISSUER) << 64) + (TOKEN))

class airdrop : public eosio::contract {
private:
	struct drop {
		account_name issuer;
		account_name token_contract;
		uint128_t primary_key() const { return PK(issuer, token_contract); }
	};

	typedef eosio::multi_index<N(drop), drop> drop_index;

public:
	airdrop(account_name self) :
		eosio::contract(self)
	{}

	void create(account_name issuer, account_name token_contract, eosio::symbol_type symbol);
	void drop(account_name issuer, account_name token_contract, eosio::symbol_type symbol, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts);
	void withdraw(account_name issuer, account_name token_contract, eosio::asset value);
};
