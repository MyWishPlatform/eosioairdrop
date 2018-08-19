import setup
import json
import csv
from termcolor import cprint
import eosf
import node
import unittest

setup.set_verbose(False)
setup.set_json(False)
setup.use_keosd(False)

class AirdropTests(unittest.TestCase):

    def run(self, result=None):
        """ Stop after first error """
        if not result.failures:
            super().run(result)

    @classmethod
    def setUpClass(cls):
        testnet = node.reset()
        assert(not testnet.error)

        global wallet
        wallet = eosf.Wallet()
        assert(not wallet.error)

        global account_master
        account_master = eosf.AccountMaster()
        wallet.import_key(account_master)
        assert(not account_master.error)

        global account_issuer
        account_issuer = eosf.account(account_master)
        wallet.import_key(account_issuer)
        assert(not account_issuer.error)

        global account_deploy_airdrop
        account_deploy_airdrop = eosf.account(account_master)
        wallet.import_key(account_deploy_airdrop)
        assert(not account_deploy_airdrop.error)

        global account_deploy_token
        account_deploy_token = eosf.account(account_master)
        wallet.import_key(account_deploy_token)
        assert(not account_deploy_token.error)

        global contract_eosio_bios
        contract_eosio_bios = eosf.Contract(account_master, "eosio.bios")
        assert(not contract_eosio_bios.error)
        deployment_bios = contract_eosio_bios.deploy()
        assert(not deployment_bios.error)

        global contract_token
        contract_token = eosf.Contract(account_deploy_token, "eosio.token")
        assert(not contract_token.error)
        deployment_token = contract_token.deploy()
        assert(not deployment_token.error)
        assert(not account_deploy_token.code().error)

        global contract_airdrop
        contract_airdrop = eosf.Contract(
                account_deploy_airdrop,
                "eosioairdrop",
                wast_file='/build/airdrop.wast',
                abi_file='/build/airdrop.abi'
        )
        assert(not contract_airdrop.error)

        deployment_airdrop = contract_airdrop.deploy()
        assert(not deployment_airdrop.error)
        assert(not account_deploy_airdrop.code().error)

    def setUp(self):
        pass

    def test_01(self):
        cprint(""" Tests for initialize """, "red")
        cprint(""" 1. Action `create` should be executed at token contract """, 'green')
        createTokenActionJSON = {
            "issuer": str(account_issuer),
            "maximum_supply": "1000000000.0000 TST",
        }

        assert(not contract_token.push_action(
                "create",
                json.dumps(createTokenActionJSON),
                account_deploy_token)
                    .error)

        cprint(""" 2. Action `create` should be executed at airdrop contract """, 'green')
        createAirdropActionJSON = {
            "issuer": str(account_issuer),
            "token_contract": str(account_deploy_token),
            "asset": "0.0000 TST"
        }

        assert(not contract_airdrop.push_action(
                "create",
                json.dumps(createAirdropActionJSON),
                account_deploy_airdrop)
                    .error)

        cprint(""" 3. Token holder should issue currency to airdrop contract """, 'green')

        issueTokenActionJSON = {
            "to": str(account_deploy_airdrop),
            "quantity": "100.0000 TST",
            "memo":"memo"
        }
        assert(not contract_token.push_action(
                "issue",
                json.dumps(issueTokenActionJSON),
                account_issuer)
                    .error)

    def test_02(self):
        cprint(""" Tests for calling methods """, "red")
        cprint(""" 4. Airdrop contract permissions should be updated """, 'green')

        airdrop_account_pubkey = account_deploy_airdrop.json["permissions"][1]["required_auth"]["keys"][0]["key"]

        permissionActionJSON = {
            "account":str(account_deploy_airdrop),
            "permission":"active",
            "parent":"owner",
            "auth":{
                "threshold":1,
                "keys":[
                    {
                        "key":str(airdrop_account_pubkey),
                        "weight":1
                    }
                ],
                "accounts":[
                    {
                        "permission":{
                            "actor":str(account_deploy_airdrop),
                            "permission":"eosio.code"
                        },
                        "weight":1
                    }
                ],
                "waits":[]
            }
        }

        setPermissionAction = json.dumps(permissionActionJSON)

        assert(not contract_eosio_bios.push_action("updateauth", setPermissionAction, account_deploy_airdrop).error)

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
            receiver = eosf.account(account_master, airdrop["address"][x])
            wallet.import_key(receiver)
            assert(not receiver.error)

        dropAirdropAction = '{"token_contract":' + str(account_deploy_token) + \
                            ', "asset": "0.0000 TST"' + \
                            ', "addresses": [' + airAddresses + \
                            '], "amounts": [' + airAmounts + ']}'

        assert(not contract_airdrop.push_action("drop", dropAirdropAction, account_issuer, output=True).error)

    def test_03(self):
        cprint(""" Tests for checking values """, "red")
        cprint(""" 6. Issuer should withdraaw tokens from airdrop contract """, 'green')

        withdrawValue = "1.0000 TST"
        withdrawAirdropAction = '{"token_contract":' + str(account_deploy_token) + \
                                ', "value": "' + withdrawValue + '"}'

        assert(not contract_airdrop.push_action("withdraw",
                                                withdrawAirdropAction,
                                                account_issuer).error)

        balanceIssuer = contract_token.table("accounts", account_issuer.name).json["rows"][0]["balance"][:-4]
        assert(balanceIssuer == withdrawValue[:-4])

        cprint(""" 7. Transferred tokens should exist on accounts """, 'green')
        decimals = 10 ** 4

        for account in range(len(airdrop["address"])):
            balance = float(contract_token.table("accounts", airdrop["address"][account]).json["rows"][0]["balance"][:-4])
            expectedBalance = int(airdrop["amount"][account]) / decimals
            assert (balance == expectedBalance)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        node.stop()

if __name__ == "__main__":
    unittest.main()