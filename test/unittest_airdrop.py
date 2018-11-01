import json
import csv
from termcolor import cprint
from eosfactory.eosf import *
import unittest
from classes import *

verbosity([Verbosity.INFO, Verbosity.OUT, Verbosity.TRACE, Verbosity.DEBUG])


class AirdropTests(unittest.TestCase):

    def run(self, result=None):
        """ Stop after first error """
        if not result.failures:
            super().run(result)

    @classmethod
    def setUpClass(cls):
        reset()
        create_wallet()
        create_master_account('master')

        COMMENT('''
        Create test accounts:
        ''')
        create_account("owner", master)
        create_account("deployer_token1", master)
        create_account("deployer_token2", master)
        create_account("deployer_airdrop", master)

        global contract_airdrop
        contract_airdrop = Contract(
            deployer_airdrop,
            "eosioairdrop",
            abi_file="build/airdrop.abi",
            wasm_file="build/airdrop.wasm"
        )
        contract_airdrop.deploy()


    def setUp(self):
        pass

    def test_01(self):
        cprint(""" Tests for initialize """, "red")
        cprint(""" 1. Action `create` should be executed at token contract """, 'green')
        global token1
        token1 = Token(1, deployer_token1, 4, "TST")
        token1.deploy()
        token1.create(owner.name)

        cprint(""" 2. Action `create` should be executed at airdrop contract """, 'green')
        global airdrop_contract
        airdrop_contract = Airdrop(deployer_airdrop)
        airdrop_contract.deploy()
        airdrop_contract.create(
            token1.pk,
            token1.owner,
            token1.account.name,
            token1.decimals,
            token1.symbol,
            10
        )

        cprint(""" 3. Token holder should issue currency to account """, 'green')
        token1.issue(airdrop_contract.account.name, 100, token1.pk)

    def test_02(self):
        cprint(""" Tests for calling methods """, "red")
        cprint(""" 4. Airdrop contract permissions should be updated """, 'green')

        # This is (i really hope) temporary fix to manually set permission "eosio.code"
        # on account of contract through pushing action "updateauth"  on system (eosio)
        # account with custom setted permission with keys because EOSFACTORY for now
        # did not implemented this functionalty yet
        airdrop_account = airdrop_contract.account
        airdrop_account_pubkey = airdrop_account.json["permissions"][1]["required_auth"]["keys"][0]["key"]
        permissionActionJSON = {
            "account": airdrop_account.name,
            "permission": "active",
            "parent": "owner",
            "auth": {
                "threshold": 1,
                "keys": [
                    {
                        "key": str(airdrop_account_pubkey),
                        "weight": 1
                    }
                ],
                "accounts": [
                    {
                        "permission": {
                            "actor": airdrop_account.name,
                            "permission": "eosio.code"
                        },
                        "weight": 1
                    }
                ],
                "waits": []
            }
        }

        master.push_action(
                "updateauth",
                permissionActionJSON,
                permission=(airdrop_account, Permission.ACTIVE))

        cprint(""" 5. Action `drop` should transfer tokens  """, 'green')
        global airdrop_csv
        with open('test/eos_airdrop.csv') as table:
            reader = csv.DictReader(table, delimiter=",", skipinitialspace=True)
            airdrop_csv = {}
            for row in reader:
                for address, amount in row.items():
                    airdrop_csv.setdefault(address, list()).append(amount)

        air_addresses = ', '.join(map('{0}'.format, airdrop_csv["address"]))
        air_amounts = ', '.join(map('{0}'.format, airdrop_csv["amount"]))

        # create accounts because you can't transfer to non-existing account, this is not ethereum lol
        for x in range(len(airdrop_csv["address"])):
            print(airdrop_csv["address"][x])
            print("receiver{}".format(x))
            receiver = create_account("receiver{}".format(x), master, airdrop_csv["address"][x])

        airdrop_contract.drop(token1.pk, token1.owner, air_addresses, air_amounts)

    def test_03(self):
        cprint(""" Tests for checking values """, "red")
        cprint(""" 6. Issuer should withdraw tokens from airdrop contract """, 'green')

        withdraw_value = "1.0000 TST"
        # withdrawAirdropAction = '{"pk": "' + withdrawPk + \
        #                         ', "token_contract":' + str(deployer_token) + \
        #                         ', "value": "' + withdrawValue + '"}'

        airdrop_contract.withdraw(token1.pk, token1.owner, withdraw_value)
        # contract_airdrop.push_action("withdraw",
        #                              {
        #                                  "pk": withdrawPk,
        #                                  "value": withdrawValue
        #                              },
        #                              permission=[(master.name, Permission.ACTIVE), (owner.name, Permission.ACTIVE)])

        balance_owner = token1.get_balance(owner)
        assert (balance_owner == withdraw_value)

        cprint(""" 7. Transferred tokens should exist on accounts """, 'green')
        decimals = 10 ** token1.decimals
        print(decimals)

        for address in range(len(airdrop_csv["address"])):
            account = airdrop_csv["address"][address]
            balance = token1.get_balance(account)
            expected_balance = int(airdrop_csv["amount"][address]) / decimals
            expected_balance_sym = "{} {}".format(expected_balance, token1.symbol)
            assert (balance == expected_balance_sym)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        stop()


if __name__ == "__main__":
    unittest.main()
