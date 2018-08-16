import sys
import setup
import json
import eosf
import node
import unittest
from termcolor import cprint
import csv

setup.set_verbose(False)
setup.set_json(False)
setup.use_keosd(False)



def test():

    testnet = node.reset()
    assert(not testnet.error)

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

    global accsreceive1
    accsreceive1 = eosf.account(account_master, "accsreceive1")
    wallet.import_key(accsreceive1)
    assert(not accsreceive1.error)

    global accsreceive2
    accsreceive2 = eosf.account(account_master, "accsreceive2")
    wallet.import_key(accsreceive2)
    assert(not accsreceive2.error)

    global accsreceive3
    accsreceive3 = eosf.account(account_master, "accsreceive3")
    wallet.import_key(accsreceive3)
    assert(not accsreceive3.error)

    account_deploy_airdrop = eosf.account(account_master)
    wallet.import_key(account_deploy_airdrop)
    assert(not account_deploy_airdrop.error)

    account_deploy_token = eosf.account(account_master)
    wallet.import_key(account_deploy_token)
    assert(not account_deploy_token.error)

    contract_eosio_bios = eosf.Contract(
        account_master, "eosio.bios").deploy()
    assert(not contract_eosio_bios.error)

    global contract_airdrop
    contract_airdrop = eosf.Contract(
            account_deploy_airdrop,
            "eosioairdrop",
            wast_file='/build/airdrop.wast',
            abi_file='/build/airdrop.abi',
            permission="eosio.code"
    )
    assert(not contract_airdrop.error)

    global contract_token
    contract_token = eosf.Contract(account_deploy_token, "eosio.token")
    assert (not contract_token.error)

    deployment = contract_token.deploy()
    assert(not deployment.error)

    cprint(""" Confirm `account_deploy_token` contains code """, 'magenta')
    assert(not account_deploy_token.code().error)

    deployment = contract_airdrop.deploy()
    assert(not deployment.error)

    cprint(""" Confirm `account_deploy_airdrop` contains code """, 'magenta')
    assert (not account_deploy_airdrop.code().error)

    createTokenAction = '{"issuer":' + str(account_issuer) + ', "maximum_supply": "1000000000.0000 TST"}'
    cprint(""" Action contract_token.push_action("create") """,'magenta')
    assert(not contract_token.push_action("create", createTokenAction, account_deploy_token).error)

    cprint(""" Action contrant_airdrop.push_action("create") """, 'magenta')
    createAirdropAction = '{"issuer":' + str(account_issuer) +\
                          ', "token_contract":' + str(account_deploy_token) +\
                          ', "asset": "0.0000 TST"}'


    assert(not contract_airdrop.push_action("create", createAirdropAction, account_deploy_airdrop).error)

    cprint(""" Action `token push action issue account_airdrop_deploy """, 'magenta')

    assert(not contract_token.push_action(
        "issue",
        '{"to":"' + str(account_deploy_airdrop) +\
        '", "quantity":"100.0000 TST", "memo":"memo"}', account_issuer).error)

    'cleos get info'
    #assert(not contract_eosio_bios.push_action("account":"))

    cprint(""" Action: `airdrop push action "drop" """, 'magenta')

    with open('test/eos_airdrop.csv') as table:
        reader = csv.DictReader(table, delimiter=",", skipinitialspace=True)
        airdrop = {}
        for row in reader:
            for address, amount in row.items():
                airdrop.setdefault(address, list()).append(amount)

    airAddresses = ', '.join(map('"{0}"'.format, airdrop["address"]))
    airAmounts = ', '.join(map('{0}'.format, airdrop["amount"]))

    dropAirdropAction = '{"token_contract":' + str(account_deploy_token) +\
                        ', "asset": "0.0000 TST"' +\
                        ', "addresses": [' + airAddresses +\
                        '], "amounts": [' + airAmounts + ']}'


    assert(not contract_airdrop.push_action("drop", dropAirdropAction, account_issuer).error)

    cprint(""" Action: `airdrop push action "withdraw" """, 'magenta')

    withdrawValue = "1.0000 TST"
    withdrawAirdropAction = '{"token_contract":' + str(account_deploy_token) + \
                            ', "value": "' + withdrawValue + '"}'
    print(withdrawAirdropAction)
    print(accsreceive1.name)
    assert(not contract_airdrop.push_action("withdraw",
                                            withdrawAirdropAction,
                                            accsreceive1).error)

    node.stop()

    cprint("OK OK OK OK OK OK OK OK 0K 0K 0K 0K", 'green')


if __name__ == "__main__":
    test()
