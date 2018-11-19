import json
import csv
from termcolor import cprint
from eosfactory.eosf import *
import unittest
from classes import *
import warnings
import argparse


class AirdropTests(unittest.TestCase):



    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                test_func(self, *args, **kwargs)
        return do_test

    def create_airdrop_accounts(self, owner, addresses):

        # create accounts because you can't transfer to non-existing account
        for x in range(len(addresses)):
            #print(airdrop_csv["address"][x])
            #print("receiver{}".format(x))
            receiver = create_account("receiver{}".format(x), owner, addresses[x])

    def run(self, result=None):
        """ Stop after first error """
        if not result.failures:
            super().run(result)

    @classmethod
    def setUpClass(cls):

        global airdrop_csv
        with open('test/eos_airdrop.csv') as table:
            reader = csv.DictReader(table, delimiter=",", skipinitialspace=True)
            airdrop_csv = {}
            for row in reader:
                for address, amount in row.items():
                    airdrop_csv.setdefault(address, list()).append(amount)
        
            global air_addresses
            air_addresses = ', '.join(map('{0}'.format, airdrop_csv["address"]))
            global air_amounts
            air_amounts = ', '.join(map('{0}'.format, airdrop_csv["amount"]))


    @classmethod
    def tearDownClass(cls):
        pass

    @ignore_warnings
    def setUp(self):
        reset()
        create_wallet()
        create_master_account('master')
        self.eosio_account = master

        create_account("owner", master)
        self.owner = owner
        create_account("deployer_token1", master)
        self.token1_account = deployer_token1
        create_account("deployer_token2", master)
        self.token2_account = deployer_token2
        create_account("deployer_airdrop", master)
        self.airdrop_account = deployer_airdrop
        create_account("buyer1", master)
        self.buyer1_acc = buyer1
        create_account("buyer2", master)
        self.buyer2_acc = buyer2

        self.main_airdrop = Airdrop(self.airdrop_account)
        self.main_airdrop.deploy()
        self.main_airdrop.add_permission(self.eosio_account)

        self.token1 = Token(
            1,
            self.owner,
            self.token1_account,
            10 ** 8,
            4,
            "EOS"
        )
        self.token1.deploy()

        self.token2 = Token(
            2,
            self.owner,
            self.token2_account,
            10 ** 8,
            4,
            "WISH"
        )
        self.token2.deploy()

        self.token1.create(self.owner, self.token1_account)
        self.token2.create(self.owner, self.token2_account)

        token1_total_str = self.token1.total_supply()
        token1_total = self.token1.fromAsset(token1_total_str)

        global amount_supply_first
        amount_supply_first = int(token1_total["amount"])

        global simple_amount_first
        simple_amount_first = self.token1.to_quantity(int(amount_supply_first / 2),self.token1.decimals,self.token1.symbol)

        global one_token_first
        one_token_first = self.token1.to_quantity(1, self.token1.decimals, self.token1.symbol)

        token2_total_str = self.token2.total_supply()
        token2_total = self.token2.fromAsset(token2_total_str)

        global amount_supply_second
        amount_supply_second = int(token2_total["amount"])

        global simple_amount_second
        simple_amount_second = self.token2.to_quantity(int(amount_supply_second / 2),self.token2.decimals,self.token2.symbol)

        global one_token_second
        one_token_second = self.token2.to_quantity(1, self.token2.decimals, self.token2.symbol)

    def tearDown(self):
        stop()

    def test_01(self):
        cprint("#1 Tests for initialize ", "magenta")
        cprint("#1.1 Check successful creating airdrop for first token", 'green')
        self.main_airdrop.create(
            self.token1.pk,
            self.token1.issuer,
            self.token1.account.name,
            self.token1.decimals,
            self.token1.symbol,
            10
        )

        cprint("#1.2 Check successful issue from system token to airdrop", 'green')
        self.token1.issue(self.main_airdrop.account.name, simple_amount_first, self.token1.pk, self.owner)

        cprint("#1.3 Check successful creating airdrop for second token", 'green')
        self.main_airdrop.create(
            self.token2.pk,
            self.token2.issuer,
            self.token2.account.name,
            self.token2.decimals,
            self.token2.symbol,
            10
        )

        cprint("#1.4 Check successful issue from custom token to airdrop", 'green')
        self.token2.issue(self.main_airdrop.account.name, simple_amount_second, self.token2.pk, self.owner)

        cprint("#1.5 Transfer from token with other PK must fail", 'green')
        with self.assertRaises(errors.Error):
            self.token1.issue(self.main_airdrop.account.name, simple_amount_first, self.token2.pk, self.owner)
        with self.assertRaises(errors.Error):
            self.token2.issue(self.main_airdrop.account.name, simple_amount_second, self.token1.pk, self.owner)


    def test_02(self):
        cprint("#1.6 Action `drop` should transfer tokens  ", 'green')
        self.main_airdrop.create(
            self.token1.pk,
            self.token1.issuer,
            self.token1.account.name,
            self.token1.decimals,
            self.token1.symbol,
            10
        )
        self.token1.issue(self.main_airdrop.account.name, simple_amount_first, self.token1.pk, self.owner)

        self.create_airdrop_accounts(master, airdrop_csv["address"])

        self.main_airdrop.drop(self.token1.pk, self.token1.issuer, air_addresses, air_amounts)


    def test_03(self):
        cprint("#2 Tests for checking values ", "magenta")
        cprint("#2.1 Issuer should withdraw tokens from airdrop contract ", 'green')

        self.main_airdrop.create(
            self.token1.pk,
            self.token1.issuer,
            self.token1.account.name,
            self.token1.decimals,
            self.token1.symbol,
            10
        )
        self.token1.issue(self.main_airdrop.account.name, simple_amount_first, self.token1.pk, self.owner)

        withdraw_value = simple_amount_first
        self.main_airdrop.withdraw(self.token1.pk, self.token1.issuer, withdraw_value)

        balance_owner = self.token1.get_balance(owner)
        assert (balance_owner == withdraw_value)

    def test_04(self):
        cprint("#2.2 Transferred tokens should exist on accounts ", 'green')
        self.main_airdrop.create(
            self.token1.pk,
            self.token1.issuer,
            self.token1.account.name,
            self.token1.decimals,
            self.token1.symbol,
            10
        )
        self.token1.issue(self.main_airdrop.account.name, simple_amount_first, self.token1.pk, self.owner)
        decimals = 10 ** self.token1.decimals
        self.create_airdrop_accounts(master, airdrop_csv["address"])
        self.main_airdrop.drop(self.token1.pk, self.token1.issuer, air_addresses, air_amounts)
        
        for address in range(len(airdrop_csv["address"])):
            account = airdrop_csv["address"][address]
            balance = self.token1.get_balance(account)
            expected_balance = int(airdrop_csv["amount"][address]) / decimals
            expected_balance_sym = "{} {}".format(expected_balance, self.token1.symbol)
            assert (balance == expected_balance_sym)

    def test_05(self):
        cprint("#2.3 Check second token on the same airdrop works correctly ", "green")
        self.main_airdrop.create(
            self.token1.pk,
            self.token1.issuer,
            self.token1.account.name,
            self.token1.decimals,
            self.token1.symbol,
            10
        )
        self.main_airdrop.create(
            self.token2.pk,
            self.token2.issuer,
            self.token2.account.name,
            self.token2.decimals,
            self.token2.symbol,
            10
        )
        self.token2.issue(self.main_airdrop.account.name, simple_amount_second, self.token2.pk, self.owner)

        self.create_airdrop_accounts(master, airdrop_csv["address"])
        self.main_airdrop.drop(self.token2.pk, self.token2.issuer, air_addresses, air_amounts)
        for address in range(len(airdrop_csv["address"])):
            account = airdrop_csv["address"][address]
            balance = self.token2.get_balance(account)
            decimals2 = 10 ** self.token2.decimals
            expected_balance = int(airdrop_csv["amount"][address]) / decimals2
            expected_balance_sym = "{} {}".format(expected_balance, self.token2.symbol)
            assert (balance == expected_balance_sym)


if __name__ == "__main__":
    verbosity([])  # disable logs

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()
    if args.verbose:
        verbosity([Verbosity.INFO, Verbosity.OUT, Verbosity.TRACE, Verbosity.DEBUG])
        print("verbosity turned on")
    unittest.main()
