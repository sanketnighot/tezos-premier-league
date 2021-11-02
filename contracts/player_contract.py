import smartpy as sp

class tplPlayer:
    def get_value_type():
        return sp.TRecord(
                player_address = sp.TAddress,
                player_nickname = sp.TString,
                display_picture = sp.TString,
                player_level = sp.TInt,
                player_tier = sp.TInt,
                player_nfts = sp.TList(sp.TNat),
                active = sp.TBool
                )

    def get_key_type():
        return sp.TAddress

class TPL_Players(sp.Contract):
    def __init__(self, admin, metadata):
        self.init(
            administrator=admin,
            metadata=metadata,
            playerLedger = sp.big_map(
                tkey= tplPlayer.get_key_type() , tvalue= tplPlayer.get_value_type()
            )
        )

    @sp.entry_point
    def addPlayer(self, params):
        self.data.playerLedger[params.player_address] = sp.record(
                            player_address = params.player_address,
                            player_nickname = params.player_nickname,
                            display_picture = params.display_picture,
                            player_level = 0,
                            player_tier = 0,
                            player_nfts = [],
                            active = True
                        )
        
    
    @sp.entry_point
    def updatePlayerNickname(self, params):
        self.data.playerLedger[params.player_address].player_nickname = params.player_nickname

    @sp.entry_point
    def updatePlayerDisplayPicture(self, params):
        self.data.playerLedger[params.player_address].display_picture = params.player_display_picture

    @sp.entry_point
    def increasePlayerLevel(self, params):
        self.data.playerLedger[params.player_address].player_level += params.value
        sp.if (self.data.playerLedger[params.player_address].player_level >= 10):
            self.data.playerLedger[params.player_address].player_level -= 10
            self.data.playerLedger[params.player_address].player_tier += 1
    
    @sp.entry_point
    def addPlayerNFTs(self, params):
        self.data.playerLedger[params.player_address].player_nfts.push(params.nft_id)

    @sp.entry_point
    def toggleActivation(self, params):
        self.data.playerLedger[params.player_address].active = ~self.data.playerLedger[params.player_address].active
    
# Test
@sp.add_test(name="TPL Player")
def test():
    sc = sp.test_scenario()
    sc.h1("TPL Players")
    sc.table_of_contents()
    sc.h2("Accounts")
    admin = sp.address("tz1LXRS2zgh12gbGix6R9xSLJwfwqM9VdpPW")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    dan = sp.test_account("Dan")
    sc.show([alice, bob, dan])
    sc.h2("TPL Players Contract")
    c1 = TPL_Players(admin=admin, metadata=sp.utils.metadata_of_url("ipfs://QmReqxsF6BTh9bLFoxFapeNFy3iS2FCxnrQPof6Tkx2T7G"))
    sc += c1

    sc.h2("Adding Player")
    sc += c1.addPlayer(sp.record(player_nickname="sanket", display_picture="sanket.png", player_address=admin)).run(sender=admin)
    
    sc.h2("Update Nickname")
    sc += c1.updatePlayerNickname(sp.record(player_nickname="sanketnighot",player_address=admin)).run(sender = admin)
    
    sc.h2("Update Display Picture")
    sc += c1.updatePlayerDisplayPicture(sp.record(player_display_picture="sanketnighot.jpg",player_address=admin)).run(sender = admin)

    sc.h2("Add NFT's")
    sc += c1.addPlayerNFTs(sp.record(nft_id= 123, player_address=admin)).run(sender=admin)
    sc += c1.addPlayerNFTs(sp.record(nft_id= 2323, player_address=admin)).run(sender=admin)
    sc += c1.addPlayerNFTs(sp.record(nft_id= 88, player_address=admin)).run(sender=admin)
    sc += c1.addPlayerNFTs(sp.record(nft_id= 56, player_address=admin)).run(sender=admin)
    sc += c1.addPlayerNFTs(sp.record(nft_id= 465, player_address=admin)).run(sender=admin)
    sc += c1.addPlayerNFTs(sp.record(nft_id= 345, player_address=admin)).run(sender=admin)

    sc.h2("Increase Player Level")
    sc += c1.increasePlayerLevel(sp.record(player_address = admin, value = 3)).run(admin)
    sc += c1.increasePlayerLevel(sp.record(player_address = admin, value = 8)).run(admin)
    sc += c1.increasePlayerLevel(sp.record(player_address = admin, value = 7)).run(admin)
    sc += c1.increasePlayerLevel(sp.record(player_address = admin, value = 5)).run(admin)
    sc += c1.increasePlayerLevel(sp.record(player_address = admin, value = 6)).run(admin)
    sc += c1.increasePlayerLevel(sp.record(player_address = admin, value = 9)).run(admin)
    
    sc.h2("Toggle Activation")
    sc += c1.toggleActivation(sp.record(player_address=admin)).run(sender=admin)
