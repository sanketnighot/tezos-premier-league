import smartpy as sp

class PlayerContract(sp.Contract):
    def __init__(self, nickname):
        self.init(
            nickname=nickname,
            nfts=sp.list(),
            level=sp.int(0),
            tier=sp.int(0),
            tokens=sp.int(0)
        )

    @sp.entry_point
    def editPlayer(self, data):
        self.data.nickname = data.nickname
        self.data.nfts.push(data.nft)

    @sp.entry_point
    def sendToken(self, data):
        # sp.verify((self.data.tokens - tkns) >= 0, message="Tokens Insufficient"​)

        player2_contract = sp.contract(sp.TInt, data.player_address, "receive_token").open_some()
        self.data.tokens -= data.tokens
        
        sp.transfer(data.tokens, sp.mutez(0), player2_contract)

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

    user1 = PlayerContract("User 1")
    user2 = PlayerContract("User 2")

    scenario += user1
    scenario += user2

    scenario += user1.handleGameLevel(10)
    scenario += user1.handleGameTier(5)
    
    scenario.verify(user1.data.nickname == "User 1" )

    data_to_be_sent = sp.record(player_address=user2.address,tokens=50)
    scenario += user1.sendToken(data_to_be_sent)

    scenario.verify(user2.data.tokens == 50)
