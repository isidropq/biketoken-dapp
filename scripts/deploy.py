#!/usr/bin/env python3
# scripts/deploy.py

import os
import json
import pathlib
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc

print("🚀 Starting deploy…")

# ── 1) Load your .env
env_path = pathlib.Path(__file__).parents[1] / ".env"
load_dotenv(env_path)
RPC = os.getenv("RPC_URL")
KEY = os.getenv("PRIVATE_KEY")
if not RPC or not KEY:
    raise RuntimeError("Missing RPC_URL or PRIVATE_KEY in .env")

# ── 2) Connect to your local chain
w3 = Web3(Web3.HTTPProvider(RPC))
acct = w3.eth.account.from_key(KEY)
chain_id = w3.eth.chain_id

# ── 3) Debug print
print("▶️ RPC_URL:", RPC)
print("▶️ PRIVATE_KEY (first 10 chars):", KEY[:10] + "…")
print("▶️ Derived address:", acct.address)
print("▶️ Balance:", w3.from_wei(w3.eth.get_balance(acct.address), "ether"), "ETH")

# ── 4) Compile all contracts in ./contracts
install_solc("0.8.20")
from pathlib import Path

contracts_dir = Path(__file__).parents[1] / "contracts"
sources = {}
for f in contracts_dir.rglob("*.sol"):
    rel = f.relative_to(contracts_dir)
    sources[str(rel)] = {"content": f.read_text()}

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": sources,
        "settings": {
            "outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}
        },
    },
    solc_version="0.8.20",
)["contracts"]

# ── 5) Deployment helper
def deploy_one(name, args=()):
    data    = compiled[f"{name}.sol"][name]
    abi     = data["abi"]
    bytecode= data["evm"]["bytecode"]["object"]
    Contract= w3.eth.contract(abi=abi, bytecode=bytecode)

    # ── FIXED: supply gas & gasPrice to avoid estimate_gas()
    tx = Contract.constructor(*args).build_transaction({
        "from":     acct.address,
        "nonce":    w3.eth.get_transaction_count(acct.address),
        "chainId":  chain_id,
        "gas":      2_000_000,              # 2 000 000 gas limit
        "gasPrice": w3.to_wei("2", "gwei"),  # 2 gwei
    })

    signed = acct.sign_transaction(tx)
    txh    = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt= w3.eth.wait_for_transaction_receipt(txh)
    return w3.eth.contract(address=receipt.contractAddress, abi=abi)

# ── 6) Deploy your two contracts
token   = deploy_one("DBSTEToken")
print("✅ DBSTE deployed at", token.address)

station = deploy_one("BikeStation", (token.address,))
print("✅ BikeStation deployed at", station.address)

# ── 7) Write ABIs out for your frontend
build_dir = pathlib.Path("build")
build_dir.mkdir(exist_ok=True)
for nm, ctr in [("DBSTEToken", token), ("BikeStation", station)]:
    with open(build_dir / f"{nm}.json", "w") as f:
        json.dump(ctr.abi, f, indent=2)

print("🚀 Deployment complete.")
