import smartpy as sp
import random

class tplGame:
    def get_value_type():
        return sp.TRecord(
                gameId = sp.TNat,
                gameName = sp.TString,
                thumbnail_url = sp.TString,
                game_added_on = sp.TNat,
                destination_url = sp.TString,
                active = sp.TBool
                )

    def get_key_type():
        return sp.TNat

class TPL_Game(sp.Contract):
    def __init__(self, admin, metadata):
        self.init(
            totalGames = 0,
            administrator=admin,
            metadata=metadata,
            gameList = sp.big_map(
                    tkey= tplGame.get_key_type() , tvalue= tplGame.get_value_type()
                )
            )
    
    @sp.entry_point
    def addGame(self, params):
        create_game = sp.record(
                                gameId = self.data.totalGames,
                                gameName = params.gameName,
                                thumbnail_url = params.thumbnail_url,
                                game_added_on = params.game_added_on,
                                destination_url = params.destination_url,
                                active = True
                                )
        self.data.gameList[self.data.totalGames] = create_game
        self.data.totalGames+=1

        
    
# Tests
@sp.add_test("TPL Game")
def test():
    sc = sp.test_scenario()
    admin = sp.address("tz1LXRS2zgh12gbGix6R9xSLJwfwqM9VdpPW")
    tpl_game = TPL_Game(admin=admin, metadata = sp.utils.metadata_of_url("ipfs://QmUBNg3gnoZFKGcSaBTBiWadVSNQ7f5pXpFyMStyjStp9U)"))
    sc += tpl_game
    mark = sp.test_account("mark")
    elon = sp.test_account("elon")
    sc.show([mark, elon])
    sc.h1("Adding Game")
    data = sp.record(
        gameName = "Game 1",
        thumbnail_url = "www.example.com",
        game_added_on = 12345,
        destination_url = "www.example.com")
    add_game = tpl_game.addGame(data)
    sc += add_game

    sc.h1("Adding Another Game")
    data2 = sp.record(
        gameName = "Game 2",
        thumbnail_url = "www.example1.com",
        game_added_on = 12345,
        destination_url = "www.example1.com")
    add_game2 = tpl_game.addGame(data2)
    sc += add_game2

    
