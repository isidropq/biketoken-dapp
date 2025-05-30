import os, json, pathlib, pytest
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc

PROJECT = pathlib.Path(__file__).resolve().parents[1]
CONTRACTS = PROJECT / "contracts"

@pytest.fixture(scope="session")
def w3():
    load_dotenv(PROJECT / ".env")
    return Web3(Web3.HTTPProvider(os.environ["RPC_URL"]))

@pytest.fixture(scope="session")
def accounts(w3):
    return w3.eth.accounts

@pytest.fixture(scope="session")
def deploy(w3, accounts):
    install_solc("0.8.20")
    sources = {p.name: p.read_text() for p in CONTRACTS.glob("*.sol")}
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {k: {"content": v} for k, v in sources.items()},
            "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
        },
        solc_version="0.8.20",
    )["contracts"]

    def _deploy(name, ctor_args=()):
        meta = compiled[f"{name}.sol"][name]
        contract = w3.eth.contract(abi=meta["abi"], bytecode=meta["evm"]["bytecode"]["object"])
        tx = contract.constructor(*ctor_args).transact({"from": accounts[0]})
        addr = w3.eth.wait_for_transaction_receipt(tx).contractAddress
        return w3.eth.contract(address=addr, abi=meta["abi"])

    token   = _deploy("DBSTEToken")
    station = _deploy("BikeStation", (token.address,))
    return token, station
