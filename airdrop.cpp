#include "airdrop.hpp"

void airdrop::create(account_name issuer, account_name token_contract, eosio::asset asset) {
	require_auth(this->_self);
	eosio::symbol_type sym = asset.symbol;
	drop_index drops(this->_self, token_contract);
	eosio_assert(drops.find(sym.name()) == drops.end(), "airdrop for this contract and symbol already exists");
	drops.emplace(this->_self, [&](auto& d) {
		d.symbol = sym;
		d.user = issuer;
	});
}

void airdrop::drop(account_name token_contract, eosio::asset asset, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts) {
	drop_index drops(this->_self, token_contract);
	auto record = drops.find(asset.symbol.name());
	eosio_assert(record != drops.end(), "Airdrop not registered");
	require_auth(record->user);

	eosio_assert(addresses.size() == amounts.size(), "Lengths not match");
	eosio::extended_asset value(asset, token_contract);
	for (int i = 0; i < addresses.size(); i++) {
		value.set_amount(amounts[i]);
		eosio::currency::inline_transfer(this->_self, addresses[i], value, "airdrop");
	}
}

void airdrop::withdraw(account_name token_contract, eosio::asset value) {
	drop_index drops(this->_self, token_contract);
	auto record = drops.find(value.symbol.name());
	eosio_assert(record != drops.end(), "Airdrop not registered");
	require_auth(record->user);

	eosio::currency::inline_transfer(this->_self, record->user, eosio::extended_asset(value, token_contract), "withdraw");
}

EOSIO_ABI(airdrop, (create)(drop)(withdraw));
