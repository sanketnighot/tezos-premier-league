import smartpy as sp

class ICC(sp.Contract):
    def __init__(self, admin, metadata):
        self.init(
            administrator = admin,
            metadata = metadata
        )

    @sp.entry_point
    def addPlayer(self, nickN, displayP):
        contractParams = sp.contract(sp.TRecord(player_nickname = sp.TString, display_picture = sp.TString),
                                        sp.address("KT1KDwbpQRx31wqGobuEQBBkrma6SgSPUNP8"),
                                        entry_point="addPlayer").open_some()
        dataToBeSent = sp.record(player_nickname = nickN, display_picture = displayP)
        sp.transfer(dataToBeSent,sp.mutez(0),contractParams)

    @sp.entry_point
    def incLevel(self, pAddress, pValue):
        contractParams = sp.contract(sp.TRecord(player_address = sp.TAddress, value = sp.TInt),
                                        sp.address("KT1KDwbpQRx31wqGobuEQBBkrma6SgSPUNP8"),
                                        entry_point="increasePlayerLevel").open_some()
        dataToBeSent = sp.record(player_address = pAddress, value = pValue)
        sp.transfer(dataToBeSent,sp.mutez(0),contractParams)


# Test
@sp.add_test(name="ICC")
def test():
    sc = sp.test_scenario()
    sc.h1("Inter Contract Calling")
    sc.table_of_contents()
    sc.h2("Accounts")
    admin = sp.address("tz1LXRS2zgh12gbGix6R9xSLJwfwqM9VdpPW")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    dan = sp.test_account("Dan")
    sc.show([alice, bob, dan])
    sc.h2("ICC Contract")
    c1 = ICC(admin=admin, metadata=sp.utils.metadata_of_url("ipfs://QmUBNg3gnoZFKGcSaBTBiWadVSNQ7f5pXpFyMStyjStp9U"))
    sc += c1

    sc.h2("Adding Player")
    sc += c1.addPlayer(nickN="sanket", displayP="sanket.png").run(sender=alice)

    sc.h2("Increase Level")
    sc += c1.incLevel(pAddress = admin, pValue = sp.int(5)).run(sender=alice)
    
