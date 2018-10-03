#include "airdrop.hpp"
#include "override.hpp"

void airdrop::on_deposit(account_name issuer, eosio::extended_asset value) {
	drop_index drops(this->_self, issuer);
	auto composite_index = drops.get_index<N(contractsymb)>();
	auto it = composite_index.find(PK(value.contract, value.symbol));
	eosio_assert(it != composite_index.end(), "No such airdrop");
	composite_index.modify(it, this->_self, [value](auto& d) {
		d.available += value;
	});
}

void airdrop::create(account_name issuer, account_name token_contract, eosio::symbol_type symbol) {
	require_auth(this->_self);
	drop_index drops(this->_self, issuer);
	auto composite_index = drops.get_index<N(contractsymb)>();
	eosio_assert(composite_index.find(PK(token_contract, symbol)) == composite_index.end(), "Airdrop already exists");
	drops.emplace(this->_self, [&](auto& d) {
		d.pk = drops.available_primary_key();
		d.available = eosio::extended_asset(eosio::asset(0, symbol), token_contract);
	});
}

void airdrop::drop(account_name issuer, account_name token_contract, eosio::symbol_type symbol, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts) {
	require_auth(issuer);

	drop_index drops(this->_self, issuer);
	auto composite_index = drops.get_index<N(contractsymb)>();

	auto record = composite_index.find(PK(token_contract, symbol));
	eosio_assert(record != composite_index.end(), "Airdrop not registered");

	eosio_assert(addresses.size() == amounts.size(), "Lengths not match");
	eosio::extended_asset value(eosio::asset(0, symbol), token_contract);
	for (int i = 0; i < addresses.size(); i++) {
			value.set_amount(amounts[i]);
			eosio::currency::inline_transfer(this->_self, addresses[i], value, "airdrop");
	}
}

void airdrop::withdraw(account_name issuer, account_name token_contract, eosio::asset value) {
	require_auth(issuer);

	drop_index drops(this->_self, issuer);
	auto composite_index = drops.get_index<N(contractsymb)>();

	auto record = composite_index.find(PK(token_contract, value.symbol));
	eosio_assert(record != composite_index.end(), "Airdrop not registered");

	eosio::currency::inline_transfer(this->_self, issuer, eosio::extended_asset(value, token_contract), "withdraw");
}
