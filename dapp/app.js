// app.js

const connectButton  = document.getElementById("connectButton");
const mintButton     = document.getElementById("mintButton");
const transferButton = document.getElementById("transferButton");
const statusDiv      = document.getElementById("status");

let web3, account;

console.log(">> app.js loaded");

connectButton.addEventListener("click", async () => {
  console.log(">> Connect Wallet clicked");
  if (!window.ethereum) {
    alert("🔌 Please install MetaMask!");
    return;
  }

  web3 = new Web3(window.ethereum);

  try {
    console.log(">> sending eth_requestAccounts");
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
    account = accounts[0];
    console.log(">> connected account:", account);
    statusDiv.innerText = `✅ Connected: ${account}`;
    mintButton.disabled = transferButton.disabled = false;
  } catch (err) {
    console.error(">> failed to connect", err);
    statusDiv.innerText = "❌ Connect failed: " + (err.message || err);
  }
});

// stub out the other buttons so you can test connect first
mintButton.addEventListener("click", () => alert("mint!"));
transferButton.addEventListener("click", () => alert("transfer!"));
