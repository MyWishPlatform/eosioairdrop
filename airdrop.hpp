#pragma once

#include <eosiolib/currency.hpp>
#include <eosiolib/vector.hpp>
#include <eosiolib/eosio.hpp>

#define PK(issuer, contract) ((static_cast<uint128_t>(issuer) << 64) | (contract))

class airdrop : public eosio::contract {
private:
	struct drop {
		uint64_t pk;
		account_name issuer;
		eosio::extended_asset available;
		uint64_t drops;

		uint64_t primary_key() const { return pk; }
		uint128_t secondary_key() const { return PK(this->issuer, this->available.contract); }
	};

	typedef eosio::multi_index<N(drop), drop, eosio::indexed_by<N(secondary), eosio::const_mem_fun<drop, uint128_t, &drop::secondary_key>>> drop_index;

	void on_deposit(uint64_t pk, eosio::extended_asset value);

public:
	airdrop(account_name self) :
		eosio::contract(self)
	{}

	void create(uint64_t pk, account_name issuer, account_name token_contract, eosio::symbol_type symbol, uint64_t drops);
	void drop(uint64_t pk, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts);
	void withdraw(uint64_t pk, eosio::asset value);

	void apply(account_name contract, uint64_t action);
};
