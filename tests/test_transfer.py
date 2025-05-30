def test_transfer_between_accounts(deploy, accounts):
    token, station = deploy
    alice, bob = accounts[0], accounts[1]

    station.functions.mintForDistance(4).transact({"from": alice})
    amount = 2 * 10**18

    bal_a_before = token.functions.balanceOf(alice).call()
    bal_b_before = token.functions.balanceOf(bob).call()

    token.functions.transfer(bob, amount).transact({"from": alice})

    assert token.functions.balanceOf(alice).call() == bal_a_before - amount
    assert token.functions.balanceOf(bob).call()   == bal_b_before + amount
