from web3 import Web3
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def Transaction(metadata_uri): 
    # Load contract ABI from a local file
    with open('abi.txt', 'r') as f:
        contract_abi = json.loads(f.read())

    # Set contract and RPC details
    contract_address = "0x8f1A6030684f975DaDfc2A8c2c52a1D5C783d492"  # Replace with your deployed contract
    infura_url = "https://sepolia.infura.io/v3/17e9e4971b4d4aff9c6db5e65cca7eef"  # Use your own project ID

    # Connect to Web3 provider
    w3 = Web3(Web3.HTTPProvider(infura_url))
    if not w3.is_connected():
        raise Exception("❌ Web3 provider not connected.")

    chain_id = w3.eth.chain_id

    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Load wallet details from .env
    minter_address = os.getenv("WALLET_ADDRESS")
    private_key = os.getenv("WALLET_PRIVATE_KEY")

    # Validate wallet setup
    if not minter_address or not private_key:
        raise Exception("❌ WALLET_ADDRESS or WALLET_PRIVATE_KEY not set in .env")

    # Prepare nonce and gas
    nonce = w3.eth.get_transaction_count(minter_address)
    gas_price = w3.eth.gas_price

    # Check for sufficient balance
    balance = w3.eth.get_balance(minter_address)
    required_gas_eth = 300000 * gas_price
    required_total = required_gas_eth + w3.to_wei(0.0001, 'ether')

    if balance < required_total:
        raise Exception(f"Insufficient funds.\nBalance: {w3.from_wei(balance, 'ether')} ETH\nRequired: {w3.from_wei(required_total, 'ether')} ETH")

    # Build the minting transaction
    transaction_data = contract.functions.publicMint(metadata_uri).build_transaction({
        'chainId': chain_id,
        'gas': 300000,
        'gasPrice': gas_price,
        'nonce': nonce,
        'from': minter_address,
        'value': w3.to_wei(0.0001, 'ether'),  # Assumes minting cost is 0.0001 ETH
    })

    # Sign the transaction with the private key
    signed_txn = w3.eth.account.sign_transaction(transaction_data, private_key)

    # Send the signed transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    # Return the transaction hash
    return tx_hash.hex()


