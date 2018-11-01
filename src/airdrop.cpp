#include "airdrop.hpp"
#include "override.hpp"

void airdrop::on_deposit(uint64_t pk, eosio::extended_asset value) {
	drop_index drop_table(this->_self, this->_self);
	auto it = drop_table.find(pk);
	eosio_assert(it != drop_table.end(), "No such airdrop");
	drop_table.modify(it, this->_self, [value](auto& d) {
		d.available += value;
	});
}

void airdrop::create(uint64_t pk, account_name issuer, account_name token_contract, eosio::symbol_type symbol, uint64_t drops) {
	require_auth(this->_self);
	drop_index drop_table(this->_self, this->_self);
	drop_table.emplace(this->_self, [&](auto& d) {
		d.pk = pk;
		d.issuer = issuer;
		d.available = eosio::extended_asset(eosio::asset(0, symbol), token_contract);
		d.drops = drops;
	});
}

void airdrop::drop(uint64_t pk, eosio::vector<account_name> addresses, eosio::vector<int64_t> amounts) {
	drop_index drop_table(this->_self, this->_self);
	auto it = drop_table.find(pk);
	eosio_assert(it != drop_table.end(), "Airdrop not registered");

	require_auth(it->issuer);

	eosio_assert(addresses.size() == amounts.size(), "Lengths not match");
	eosio_assert(addresses.size() <= it->drops, "Too much targets");

	int64_t total_amount = it->available.amount;
	eosio::extended_asset value(eosio::asset(0, it->available.symbol), it->available.contract);
	for (int i = 0; i < addresses.size(); i++) {
		total_amount -= amounts[i];
		value.set_amount(amounts[i]);
		eosio::currency::inline_transfer(this->_self, addresses[i], value, "Airdrop");
	}

	eosio_assert(total_amount >= 0, "Not enough tokens on balance");

	drop_table.modify(it, it->issuer, [&](auto& d) {
		d.drops -= addresses.size();
		d.available.set_amount(total_amount);
	});
}

void airdrop::withdraw(uint64_t pk, eosio::asset value) {
	drop_index drop_table(this->_self, this->_self);
	auto it = drop_table.find(pk);
	eosio_assert(it != drop_table.end(), "Airdrop not registered");

	require_auth(it->issuer);

	drop_table.modify(it, it->issuer, [&](auto& d) {
		d.available -= value;
	});

	eosio_assert(it->available.amount >= 0, "Not enough tokens on balance");

	eosio::currency::inline_transfer(this->_self, it->issuer, eosio::extended_asset(value, it->available.contract), "Withdraw");
}
