import smartpy as sp

# Import FA2 template
FA12 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA1.2.py")
# Define PLAY_token
class PLAY_token(FA12.FA12):
    FA12.TZIP16_Metadata_Base = {
    "name"          : "TPL PLAY Token",
    "description"   : "A Native token for interacting with TPL Platform",
    "authors"       : [
        "Sanket Nighot <sanketnighot25@gmail.com>",
        "Ayush Yadav <aayush.sang@gmail.com>"
    ],
    "homepage"      : "Comming Soon",
    "interfaces"    : [
        "TZIP-007-2021-04-17",
        "TZIP-016-2021-04-17"
    ],
}
    def __init__(self, admin_address):
        super().__init__(
            admin_address,
            config=FA12.FA12_config(support_upgradable_metadata=True),
            token_metadata={
                "decimals": "0",  # Mandatory by the spec
                "name": "Play Token",  # Recommended
                "symbol": "PLAY",  # Recommended
            },
        )

    @sp.entry_point
    def mint(self, params):
        sp.set_type(params, sp.TRecord(address=sp.TAddress, value=sp.TNat))
        self.addAddressIfNecessary(params.address)
        self.data.balances[params.address].balance += params.value
        self.data.totalSupply += params.value

    @sp.entry_point
    def burn(self, params):
        sp.set_type(params, sp.TRecord(address=sp.TAddress, value=sp.TNat))
        sp.verify(
            self.data.balances[params.address].balance >= params.value,
            message="Error: InsufficientBalance",
        )
        self.data.balances[params.address].balance = sp.as_nat(
            self.data.balances[params.address].balance - params.value
        )
        self.data.totalSupply = sp.as_nat(self.data.totalSupply - params.value)


@sp.add_test(name="Fungible Token")
def test():
    scenario = sp.test_scenario()

    admin = sp.address("tz1LXRS2zgh12gbGix6R9xSLJwfwqM9VdpPW")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Robert")

    # Initialize PLAY_TOKEN as PLAY_TOKEN with single_asset = True
    PLAY_TOKEN = PLAY_token(admin)
    scenario += PLAY_TOKEN

    scenario.h1("Entry points")
    scenario.h2("Admin mints a few coins")
    PLAY_TOKEN.mint(address=alice.address, value=12).run(sender=admin)
    PLAY_TOKEN.mint(address=alice.address, value=3).run(sender=admin)
    PLAY_TOKEN.mint(address=alice.address, value=3).run(sender=admin)
    scenario.h2("Alice transfers to Bob")
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=4).run(
        sender=alice
    )
    scenario.verify(PLAY_TOKEN.data.balances[alice.address].balance == 14)
    scenario.h2("Bob tries to transfer from Alice but he doesn't have her approval")
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=4).run(
        sender=bob, valid=False
    )
    scenario.h2("Alice approves Bob and Bob transfers")
    PLAY_TOKEN.approve(spender=bob.address, value=5).run(sender=alice)
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=4).run(sender=bob)
    scenario.h2("Bob tries to over-transfer from Alice")
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=4).run(
        sender=bob, valid=False
    )
    scenario.h2("Admin burns Bob token")
    PLAY_TOKEN.burn(address=bob.address, value=1).run(sender=admin)
    scenario.verify(PLAY_TOKEN.data.balances[alice.address].balance == 10)
    scenario.h2("Alice tries to burn Bob token")
    PLAY_TOKEN.burn(address=bob.address, value=1).run(sender=alice, valid=False)
    scenario.h2("Admin pauses the contract and Alice cannot transfer anymore")
    PLAY_TOKEN.setPause(True).run(sender=admin)
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=4).run(
        sender=alice, valid=False
    )
    scenario.verify(PLAY_TOKEN.data.balances[alice.address].balance == 10)
    scenario.h2("Admin transfers while on pause")
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=1).run(
        sender=admin
    )
    scenario.h2("Admin unpauses the contract and transferts are allowed")
    PLAY_TOKEN.setPause(False).run(sender=admin)
    scenario.verify(PLAY_TOKEN.data.balances[alice.address].balance == 9)
    PLAY_TOKEN.transfer(from_=alice.address, to_=bob.address, value=1).run(
        sender=alice
    )

    scenario.show(PLAY_TOKEN.data.totalSupply)
    scenario.verify(PLAY_TOKEN.data.balances[alice.address].balance == 8)
    scenario.verify(PLAY_TOKEN.data.balances[bob.address].balance == 9)
