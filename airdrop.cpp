#include "airdrop.hpp"

void airdrop::create(account_name issuer, account_name token_contract, eosio::symbol_type symbol) {
	require_auth(this->_self);
	drop_index drops(this->_self, symbol.name());
	eosio_assert(drops.find(PK(issuer, token_contract)) == drops.end(), "Airdrop for this contract and symbol already exists");
	drops.emplace(this->_self, [&](auto& d) {
		d.issuer = issuer;
		d.token_contract = token_contract;
	});
}

void airdrop::drop(account_name issuer, account_name token_contract, eosio::symbol_type symbol, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts) {
	require_auth(issuer);

	drop_index drops(this->_self, symbol.name());
	auto record = drops.find(PK(issuer, token_contract));
	eosio_assert(record != drops.end(), "Airdrop not registered");

	eosio_assert(addresses.size() == amounts.size(), "Lengths not match");
	eosio::extended_asset value(eosio::asset(0, symbol), token_contract);
	for (int i = 0; i < addresses.size(); i++) {
		value.set_amount(amounts[i]);
		eosio::currency::inline_transfer(this->_self, addresses[i], value, "airdrop");
	}
}

void airdrop::withdraw(account_name issuer, account_name token_contract, eosio::asset value) {
	require_auth(issuer);

	drop_index drops(this->_self, value.symbol.name());
	auto record = drops.find(PK(issuer, token_contract));
	eosio_assert(record != drops.end(), "Airdrop not registered");

	eosio::currency::inline_transfer(this->_self, issuer, eosio::extended_asset(value, token_contract), "withdraw");
}

EOSIO_ABI(airdrop, (create)(drop)(withdraw));
