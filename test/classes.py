from eosfactory.eosf import *

class Token:
    owner = None
    pk = None
    account = None
    decimals = None
    symbol = None
    contract = None

    def __init__(self, token_id, token_account, token_decimals, token_symbol):
        self.pk = str(token_id)
        self.account = token_account
        self.decimals = token_decimals
        self.symbol = token_symbol

    def deploy(self):
        self.contract = Contract(
            self.account.name,
            "eosio.token",
            abi_file="eosio.token.abi",
            wasm_file="eosio.token.wasm"
        )
        self.contract.deploy()

    def create(self, token_owner):
        self.owner = token_owner
        self.account.push_action(
            "create",
                {
                    "issuer": self.owner,
                    "maximum_supply": "1000000000.0000 {}".format(self.symbol)
                },
                permission=(self.account, Permission.ACTIVE)
        )

    def issue(self, to, amount, memo):
        self.account.push_action(
            "issue",
                {
                    "to":       to,
                    "quantity": "{}.0000 {}".format(amount, self.symbol),
                    "memo":     memo
                },
                permission=(self.owner, Permission.ACTIVE)
        )

    # account should passed as namestring, e.g. account.name if not checking raw address
    def get_balance(self, user_account):
        return self.account.table("accounts", user_account).json["rows"][0]["balance"]

class Airdrop:
    account = None
    contract = None

    def __init__(self, airdrop_account):
        self.account = airdrop_account

    def deploy(self):
       self.contract = Contract(
            self.account.name,
            "eosioairdrop",
            abi_file="build/airdrop.abi",
            wasm_file="build/airdrop.wasm"
        )
       self.contract.deploy()

    def create(self, token_pk, token_owner, token_contract, decimals, symbol, records):
        self.account.push_action(
            "create",
                {
                    "pk": token_pk,
                    "issuer": token_owner,
                    "token_contract": token_contract,
                    "symbol": "{},{}".format(decimals, symbol),
                    "drops": records
                },
                permission=(self.account, Permission.ACTIVE)
        )

    def drop(self, pk, owner, addresses, amounts):
        dropAction = '{"pk": "' + pk + \
                     '", "addresses": [' + addresses + \
                     '], "amounts": [' + amounts + ']}'
        self.account.push_action(
            "drop",
            dropAction,
            permission=(owner, Permission.ACTIVE)
        )
    def withdraw(self, pk, owner, value):
        self.account.push_action(
            "withdraw",
                {
                    "pk": pk,
                    "value": value
                },
                permission=(owner, Permission.ACTIVE)
        )
