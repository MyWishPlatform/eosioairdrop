import json
import csv
from termcolor import cprint
from eosfactory.eosf import *
import unittest

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
        create_account("deployer_token", master)
        create_account("deployer_airdrop", master)

        global contract_token
        contract_token = Contract(
            deployer_token,
            "eosio.token",
            abi_file="eosio.token.abi",
            wasm_file="eosio.token.wasm"
        )
        contract_token.deploy()

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
        contract_token.push_action(
            "create",
                {
                    "issuer": owner,
                    "maximum_supply": "1000000000.0000 TST"
                },
                permission=[(master.name, Permission.ACTIVE), (deployer_token.name, Permission.ACTIVE)])


        cprint(""" 2. Action `create` should be executed at airdrop contract """, 'green')
        contract_airdrop.push_action(
            "create",
                {
                    "issuer": owner,
                    "token_contract": deployer_token,
                    "asset": "0.0000 TST"
                },
                permission=[(master.name, Permission.ACTIVE), (deployer_airdrop.name, Permission.ACTIVE)])

        cprint(""" 3. Token holder should issue currency to airdrop contract """, 'green')
        contract_token.push_action(
            "issue",
                {
                    "to":       deployer_airdrop.name,
                    "quantity": "100.0000 TST",
                    "memo":     "memo"
                },
                permission=[(master.name, Permission.ACTIVE), (owner.name, Permission.ACTIVE)])

    def test_02(self):
        cprint(""" Tests for calling methods """, "red")
        cprint(""" 4. Airdrop contract permissions should be updated """, 'green')

        airdrop_account_pubkey = deployer_airdrop.json["permissions"][1]["required_auth"]["keys"][0]["key"]
        permissionActionJSON = {
            "account": deployer_airdrop.name,
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
                            "actor": deployer_airdrop.name,
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
                permission=(deployer_airdrop.name, Permission.ACTIVE))

        cprint(""" 5. Action `drop` should transfer tokens  """, 'green')
        global airdrop
        with open('test/eos_airdrop.csv') as table:
            reader = csv.DictReader(table, delimiter=",", skipinitialspace=True)
            airdrop = {}
            for row in reader:
                for address, amount in row.items():
                    airdrop.setdefault(address, list()).append(amount)

        airAddresses = ', '.join(map('{0}'.format, airdrop["address"]))
        airAmounts = ', '.join(map('{0}'.format, airdrop["amount"]))

        # create accounts because you can't transfer to account that doesn't exist
        for x in range(len(airdrop["address"])):
            print(airdrop["address"][x])
            print("receiver{}".format(x))
            receiver = create_account("receiver{}".format(x), master, airdrop["address"][x])

        dropAirdropAction = '{"token_contract":' + deployer_token.name + \
                            ', "asset": "0.0000 TST"' + \
                            ', "addresses": [' + airAddresses + \
                            '], "amounts": [' + airAmounts + ']}'

        contract_airdrop.push_action(
            "drop",
            dropAirdropAction,
            permission=(owner.name, Permission.ACTIVE))

    def test_03(self):
        cprint(""" Tests for checking values """, "red")
        cprint(""" 6. Issuer should withdraw tokens from airdrop contract """, 'green')

        withdrawValue = "1.0000 TST"
        withdrawAirdropAction = '{"token_contract":' + str(deployer_token) + \
                                ', "value": "' + withdrawValue + '"}'

        contract_airdrop.push_action("withdraw",
                                     withdrawAirdropAction,
                                     permission=[(master.name, Permission.ACTIVE), (owner.name, Permission.ACTIVE)])

        balanceIssuer = contract_token.table("accounts", owner.name).json["rows"][0]["balance"][:-4]
        assert (balanceIssuer == withdrawValue[:-4])

        cprint(""" 7. Transferred tokens should exist on accounts """, 'green')
        decimals = 10 ** 4

        for account in range(len(airdrop["address"])):
            balance = float(
                contract_token.table("accounts", airdrop["address"][account]).json["rows"][0]["balance"][:-4])
            expectedBalance = int(airdrop["amount"][account]) / decimals
            assert (balance == expectedBalance)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        stop()


if __name__ == "__main__":
    unittest.main()
