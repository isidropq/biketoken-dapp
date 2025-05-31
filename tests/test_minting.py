import csv, pathlib, pytest
TOKENS_PER_KM = 1_000000000000000000  # 1 ether

def read_rides():
    with (pathlib.Path(__file__).parent / "data/rides.csv").open() as f:
        return list(csv.DictReader(f))

def test_mint_for_distance(deploy, accounts, w3):
    token, station = deploy
    rides = read_rides()

    for ride in rides:
        rider = accounts[int(ride["account"])]
        km = int(ride["distance_km"])
        if km == 0:
            with pytest.raises(ValueError):
                station.functions.mintForDistance(km).transact({"from": rider})
            continue
        bal_before = token.functions.balanceOf(rider).call()
        station.functions.mintForDistance(km).transact({"from": rider})
        bal_after  = token.functions.balanceOf(rider).call()
        assert bal_after - bal_before == km * TOKENS_PER_KM
