from web3 import Web3
from web3.auto import w3
import os
import pickle
from dotenv import load_dotenv,find_dotenv
from web3.middleware import geth_poa_middleware
from eth_account import Account
load_dotenv(find_dotenv) 
infura_key = os.environ.get('INFURA_KEY')
private_key_hex = os.environ.get("PRIVATE_KEY_HEX")
contract_address  = os.environ.get("CONTRACT_ADDRESS")

# Set up Web3 connection
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/"+infura_key)) # Replace with your own RPC endpoint

# Replace with your own contract ABI
contract_abi = [
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "context",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "bytes",
				"name": "bytesHTTPReq",
				"type": "bytes"
			}
		],
		"name": "get_request",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "context",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "bytes",
				"name": "bytesHTTPRes",
				"type": "bytes"
			}
		],
		"name": "get_response",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "context",
				"type": "string"
			},
			{
				"internalType": "bytes",
				"name": "bytesHTTPReq",
				"type": "bytes"
			}
		],
		"name": "request_handler",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "context",
				"type": "string"
			},
			{
				"internalType": "bytes",
				"name": "bytesHTTPRes",
				"type": "bytes"
			}
		],
		"name": "response_handler",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

event_filter = contract.events.get_request.create_filter(fromBlock='latest')

# Set up account
account = w3.eth.account.from_key(private_key_hex)

# Define function to listen to event and process arguments
def process_event():
    while True:
        event_logs = event_filter.get_new_entries()
        for event_log in event_logs:
          bytesHTTPReq = event_log['args']["bytesHTTPReq"]
          context =  event_log['args']['context']
          
          jsonHTTPReq = pickle.loads(bytesHTTPReq)
          actualHTTPReq = json.loads(jsonHTTPReq)
          response = requests.request(method=actualHTTPReq.method, url=actualHTTPReq.url, headers=actualHTTPReq.headers, data=actualHTTPReq.data)
          bytesHTTPRes = pickle.dumps(response)
          tx_hash = contract.functions.response_handler(context,bytesHTTPRes).build_transaction({
              'gas': 2000000,
              'gasPrice': web3.to_wei('50', 'gwei'),
              'nonce': web3.eth.get_transaction_count(account.address)
          })
          signed_tx = account.signTransaction(tx_hash)
          tx_receipt = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
          print(f"Transaction sent with tx_hash: {tx_receipt.hex()}")

process_event()