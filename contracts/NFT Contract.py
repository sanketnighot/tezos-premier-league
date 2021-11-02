import smartpy as sp

class FA2ErrorMessage:
    PREFIX = "FA2_"
    TOKEN_UNDEFINED = "{}TOKEN_UNDEFINED".format(PREFIX)
    INSUFFICIENT_BALANCE = "{}INSUFFICIENT_BALANCE".format(PREFIX)
    NOT_OWNER = "{}NOT_OWNER".format(PREFIX)
    OPERATORS_UNSUPPORTED = "{}OPERATORS_UNSUPPORTED".format(PREFIX)


class TPLErrorMessage:
    PREFIX = "TPL_"
    CREATION_LIMIT_EXCEEDED = "{}CREATION_LIMIT_EXCEEDED".format(PREFIX)
    CANT_MINT_SAME_TOKEN_TWICE = "{}CANT_MINT_SAME_TOKEN_TWICE".format(PREFIX)
    CONTRACT_IS_PAUSED = "{}CONTRACT_IS_PAUSED".format(PREFIX)
    MIN_VALUE_SHOULD_BE_MORE_THAN_ZERO = "{}MIN_VALUE_SHOULD_BE_MORE_THAN_ZERO".format(
        PREFIX)
    INCORRECT_PURCHASE_VALUE = "{}INCORRECT_PURCHASE_VALUE".format(PREFIX)


class LedgerKey:
    def get_type():
        return sp.TRecord(owner=sp.TAddress, token_id=sp.TNat).layout(("owner", "token_id"))

    def make(owner, token_id):
        return sp.set_type_expr(sp.record(owner=owner, token_id=token_id), LedgerKey.get_type())


class TokenValue:
    def get_type():
        return sp.TRecord(global_card_id=sp.TNat, player_id=sp.TNat, type=sp.TString, ipfs_string=sp.TString).layout(("global_card_id", ("player_id", ("type", ("ipfs_string")))))


class TokenMetadataValue:
    def get_type():
        return sp.TRecord(
            token_id=sp.TNat,
            token_info=sp.TMap(sp.TString, sp.TBytes)
        ).layout(("token_id", "token_info"))


class marketplace:
    """
    type marketplace = {
        key = nat : {
            seller = address,
            sale_value = mutez
        }
    }
    """

    def get_value_type():
        return sp.TRecord(
            seller=sp.TAddress,
            sale_value=sp.TMutez,
        )

    def get_key_type():
        """ TPL Token ID """
        return sp.TNat


class BatchTransfer:
    def get_transfer_type():
        tx_type = sp.TRecord(to_=sp.TAddress,
                             token_id=sp.TNat,
                             amount=sp.TNat).layout(
            ("to_", ("token_id", "amount"))
        )
        transfer_type = sp.TRecord(from_=sp.TAddress,
                                   txs=sp.TList(tx_type)).layout(
                                       ("from_", "txs"))
        return transfer_type

    def get_type():
        return sp.TList(BatchTransfer.get_transfer_type())

    def item(from_, txs):
        return sp.set_type_expr(sp.record(from_=from_, txs=txs), BatchTransfer.get_transfer_type())


class MultipleIPFSList:
    def get_type():
        return sp.TList(sp.TString)


class BalanceOfRequest:
    def get_response_type():
        return sp.TList(
            sp.TRecord(
                request=LedgerKey.get_type(),
                balance=sp.TNat).layout(("request", "balance")))

    def get_type():
        return sp.TRecord(
            requests=sp.TList(LedgerKey.get_type()),
            callback=sp.TContract(BalanceOfRequest.get_response_type())
        ).layout(("requests", "callback"))


class OperatorParam:
    def get_type():
        t = sp.TRecord(
            owner=sp.TAddress,
            operator=sp.TAddress,
            token_id=sp.TNat
        ).layout(("owner", ("operator", "token_id")))

        return t

    def make(owner, operator, token_id):
        r = sp.record(owner=owner,
                      operator=operator,
                      token_id=token_id)
        return sp.set_type_expr(r, OperatorParam.get_type())

class TPL_NFT(sp.Contract):
    def __init__(self, admin, metadata):
        self.init(
            ledger=sp.big_map(tkey=LedgerKey.get_type(), tvalue=sp.TNat),
            token_metadata=sp.big_map(
                tkey=sp.TNat, tvalue=TokenMetadataValue.get_type()),
            paused=False,
            administrator=admin,
            metadata=metadata,
            all_tokens=sp.set(t=sp.TNat),
            tokens=sp.big_map(tkey=sp.TNat, tvalue=TokenValue.get_type()),
            marketplace=sp.big_map(
                tkey=marketplace.get_key_type(), tvalue=marketplace.get_value_type())
        )

        self.add_flag("initial-cast")

    def is_administrator(self, sender):
        return sender == self.data.administrator

    @sp.entry_point
    def set_administrator(self, params):
        sp.verify(self.is_administrator(sp.sender),
                  message=FA2ErrorMessage.NOT_OWNER)
        self.data.administrator = params

    def is_paused(self):
        return self.data.paused

    @sp.entry_point
    def set_pause(self, params):
        sp.verify(self.is_administrator(sp.sender),
                  message=FA2ErrorMessage.NOT_OWNER)
        self.data.paused = params

    @sp.entry_point
    def mint(self, params):
        sp.verify(~self.is_paused(), TPLErrorMessage.CONTRACT_IS_PAUSED)
        sp.verify(self.is_administrator(sp.sender),
                  message=FA2ErrorMessage.NOT_OWNER)
        token_id = sp.len(self.data.all_tokens)
        sp.verify(~ self.data.all_tokens.contains(token_id),
                  message=TPLErrorMessage.CANT_MINT_SAME_TOKEN_TWICE)
        sp.set_type(params.metadata, sp.TMap(sp.TString, sp.TBytes))
        user = LedgerKey.make(sp.sender, token_id)
        self.data.ledger[user] = 1
        self.data.token_metadata[token_id] = sp.record(
            token_id=token_id, token_info=params.metadata)
        self.data.tokens[token_id] = sp.record(global_card_id=token_id, player_id=params.player_id,
                                            type=params.type, ipfs_string=params.ipfs_string)
        self.data.all_tokens.add(token_id)

    @sp.entry_point
    def transfer(self, batch_transfers):
        sp.verify(~self.is_paused(), TPLErrorMessage.CONTRACT_IS_PAUSED)
        sp.set_type(batch_transfers, BatchTransfer.get_type())
        sp.for transfer in batch_transfers:
            sp.for tx in transfer.txs:
                sp.if (tx.amount > sp.nat(0)):
                    from_user = LedgerKey.make(transfer.from_, tx.token_id)
                    to_user = LedgerKey.make(tx.to_, tx.token_id)
                    sp.verify(self.data.all_tokens.contains(
                        tx.token_id), FA2ErrorMessage.TOKEN_UNDEFINED)
                    sp.verify((self.data.ledger[from_user] >= tx.amount),
                              message=FA2ErrorMessage.INSUFFICIENT_BALANCE)
                    sp.verify((sp.sender == transfer.from_) | (
                        sp.source == transfer.from_), message=FA2ErrorMessage.NOT_OWNER)
                    self.data.ledger[from_user] = sp.as_nat(
                        self.data.ledger[from_user] - tx.amount)
                    self.data.ledger[to_user] = self.data.ledger.get(
                        to_user, 0) + tx.amount
                sp.if self.data.marketplace.contains(tx.token_id):
                    del self.data.marketplace[tx.token_id]

    @sp.entry_point
    def list_card_on_marketplace(self, params):
        sp.verify(~self.is_paused(), TPLErrorMessage.CONTRACT_IS_PAUSED)
        sp.set_type(params.token_id, sp.TNat)
        sp.set_type(params.sale_price, sp.TMutez)
        from_user = LedgerKey.make(sp.sender, params.token_id)
        sp.verify(self.data.all_tokens.contains(
            params.token_id), FA2ErrorMessage.TOKEN_UNDEFINED)
        sp.verify(params.sale_price > sp.mutez(0),
                  TPLErrorMessage.MIN_VALUE_SHOULD_BE_MORE_THAN_ZERO)
        sp.verify(self.data.ledger.contains(from_user),
                  message=FA2ErrorMessage.NOT_OWNER)
        sp.verify((self.data.ledger.get(from_user, sp.nat(0)) >= 1),
                  message=FA2ErrorMessage.INSUFFICIENT_BALANCE)
        self.data.marketplace[params.token_id] = sp.record(
            seller=sp.sender,
            sale_value=params.sale_price
        )

    @sp.entry_point
    def withdraw_card_from_marketplace(self, params):
        sp.verify(~self.is_paused(), TPLErrorMessage.CONTRACT_IS_PAUSED)
        sp.set_type(params.token_id, sp.TNat)
        from_user = LedgerKey.make(sp.sender, params.token_id)
        sp.verify(self.data.all_tokens.contains(
            params.token_id), FA2ErrorMessage.TOKEN_UNDEFINED)
        sp.verify(self.data.marketplace.contains(
            params.token_id), FA2ErrorMessage.TOKEN_UNDEFINED)
        sp.verify(self.data.ledger.contains(from_user),
                  message=FA2ErrorMessage.NOT_OWNER)
        sp.verify((self.data.ledger.get(from_user, sp.nat(0)) >= 1),
                  message=FA2ErrorMessage.INSUFFICIENT_BALANCE)
        del self.data.marketplace[params.token_id]

    @sp.entry_point
    def buy_card_from_marketplace(self, params):
        sp.verify(~self.is_paused(), TPLErrorMessage.CONTRACT_IS_PAUSED)
        sp.set_type(params.token_id, sp.TNat)
        sp.verify(self.data.all_tokens.contains(
            params.token_id), FA2ErrorMessage.TOKEN_UNDEFINED)
        sp.verify(self.data.marketplace.contains(
            params.token_id), FA2ErrorMessage.TOKEN_UNDEFINED)
        sp.verify(self.data.marketplace[params.token_id].sale_value ==
                  sp.amount, TPLErrorMessage.INCORRECT_PURCHASE_VALUE)
        seller = LedgerKey.make(
            self.data.marketplace[params.token_id].seller, params.token_id)
        buyer = LedgerKey.make(sp.sender, params.token_id)
        self.data.ledger[seller] = sp.as_nat(
            self.data.ledger[seller] - 1)
        self.data.ledger[buyer] = 1
        sp.send(self.data.marketplace[params.token_id].seller, sp.amount)
        del self.data.marketplace[params.token_id]

    @sp.entry_point
    def balance_of(self, balance_of_request):
        sp.verify(~self.is_paused(), TPLErrorMessage.CONTRACT_IS_PAUSED)
        sp.set_type(balance_of_request, BalanceOfRequest.get_type())
        responses = sp.local("responses", sp.set_type_expr(
            sp.list([]), BalanceOfRequest.get_response_type()))
        sp.for request in balance_of_request.requests:
            responses.value.push(sp.record(request=request, balance=self.data.ledger.get(
                LedgerKey.make(request.owner, request.token_id), 0)))
        sp.transfer(responses.value, sp.mutez(0), balance_of_request.callback)

    @sp.entry_point
    def update_operators(self, params):
        sp.set_type(params, sp.TList(
            sp.TVariant(
                add_operator=OperatorParam.get_type(),
                remove_operator=OperatorParam.get_type())))
        sp.failwith(FA2ErrorMessage.OPERATORS_UNSUPPORTED)


if "templates" not in __name__:
    @sp.add_test(name="TPL NFT")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("TPL NFT and Marketplace")
        scenario.table_of_contents()
        scenario.h2("Accounts")
        admin = sp.address("tz1LXRS2zgh12gbGix6R9xSLJwfwqM9VdpPW")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Bob")
        dan = sp.test_account("Dan")
        scenario.show([alice, bob, dan])
        scenario.h2("TPL NFT Contract")
        c1 = TPL_NFT(admin=admin, metadata=sp.utils.metadata_of_url("ipfs://QmUBNg3gnoZFKGcSaBTBiWadVSNQ7f5pXpFyMStyjStp9U"))
        scenario += c1
        scenario.h2("Initiate initial minting")
        scenario += c1.mint(metadata={'': sp.utils.bytes_of_string('x')}, player_id=0, type="Standard",
                            ipfs_string="ipfs://QmVdbn8QvAADa5ydnqn4dwRdixJiaCHgrWhrxsZ56ZK2vY").run(sender=admin)
        scenario += c1.mint(metadata={'': sp.utils.bytes_of_string('z')}, player_id=0, type="Standard",
                            ipfs_string="ipfs://QmVdbn8QvAADa5ydnqn4dwRdixJiaCHgrWhrxsZ56ZK2vY").run(sender=admin)
        scenario += c1.mint(metadata={'': sp.utils.bytes_of_string('q')}, player_id=0, type="Standard",
                            ipfs_string="ipfs://QmVdbn8QvAADa5ydnqn4dwRdixJiaCHgrWhrxsZ56ZK2vY").run(sender=admin)
        scenario += c1.mint(metadata={'': sp.utils.bytes_of_string('w')}, player_id=0, type="Standard",
                            ipfs_string="ipfs://QmVdbn8QvAADa5ydnqn4dwRdixJiaCHgrWhrxsZ56ZK2vY").run(sender=admin)
        scenario += c1.mint(metadata={'': sp.utils.bytes_of_string('e')}, player_id=0, type="Standard",
                            ipfs_string="ipfs://QmVdbn8QvAADa5ydnqn4dwRdixJiaCHgrWhrxsZ56ZK2vY").run(sender=admin)
