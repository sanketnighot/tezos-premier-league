import smartpy as sp

class PlayerContract(sp.Contract):
    def __init__(self, nickname):
        self.init(
            nickname=nickname,
            nfts=sp.list(),
            level=sp.nat(0),
            tier=sp.nat(0),
            tokens=sp.nat(0)
        )

    @sp.entry_point
    def editPlayer(self, nickname,nft):
        self.data.nickname = nickname
        self.data.nfts.push(nft)

    @sp.entry_point
    def sendToken(self, player_address, tokens):
        # sp.verify((self.data.tokens - tokens) >= 0, message="Tokens Insufficient"​)

        data_type = sp.TRecord(tokens=sp.TNat, player_contract=sp.TContract(sp.TNat))
        player2_contract = sp.contract(data_type, player_address, "receive_token").open_some()
        self.data.tokens -= tokens

        sp.transfer(tokens, sp.mutez(0), player2_contract)

    @sp.entry_point
    def receive_token(self, tokens):
        self.data.tokens += tokens

    @sp.entry_point
    def handleGameLevel(self, level):
        self.data.level = level

    @sp.entry_point
    def handleGameTier(self, tier):
        self.data.tier = tier
    
    
    # @sp.entry_point
    # def viewTokenBalance(self):
    #     self.data.storedValue = value

    # @sp.entry_point
    # def viewPlayerProfile(self, value):
    #     self.data.storedValue = value

    # @sp.entry_point
    # def addPlayer(self, value):
    #   self.data.value = value

    # @sp.entry_point
    # def removePlayer(self, value):
    #   self.data.value = value


@sp.add_test(name="PlayerContract")
def test():
    scenario = sp.test_scenario()


# A a compilation target (produces compiled code)
# sp.add_compilation_target("player_contract_compiled", PlayerContract())
