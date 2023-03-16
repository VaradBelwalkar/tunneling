from web3 import Web3
from web3.auto import w3
import os
import pickle
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
import random
from eth_account import Account
load_dotenv() 
infura_key = os.environ.get('INFURA_KEY')
private_key_hex = os.environ.get("PRIVATE_KEY")
contract_address  = os.environ.get("CONTRACT_ADDRESS")
# Set up Web3 connection
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/"+infura_key)) # Replace with your own RPC endpoint

# Set up contract instance and event filter
# Replace with your own contract ABI
contract_abi = [
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "filterValue",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "HTTPObj",
				"type": "string"
			}
		],
		"name": "get_request",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "filterValue",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "HTTPObj",
				"type": "string"
			}
		],
		"name": "get_response",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "filterValue",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "HTTPObj",
				"type": "string"
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
				"name": "filterValue",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "HTTPObj",
				"type": "string"
			}
		],
		"name": "response_handler",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


account = w3.eth.account.from_key(private_key_hex)


def createUniqueContext():
    return random.randint(1,10000)


# Define function to listen to event and process arguments
def forward_to_contract(HTTPReq):
     bytesHTTPReq = pickle.dumps(HTTPReq)
     context = createUniqueContext()
     event_filter = contract_client.events.get_response.createFilter(fromBlock='latest',argument_filters={'id':context})
    tx_hash = contract.functions.request_handler(string(context),bytesHTTPReq).build_transaction({
    'gas': 2000000,
    'gasPrice': web3.to_wei('50', 'gwei'),
    'nonce': web3.eth.get_transaction_count(account.address)
     })
     signed_tx = account.signTransaction(tx_hash)
     tx_receipt = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
     print(f"Transaction sent with tx_hash: {tx_receipt.hex()}")
    while True:
        event_logs = event_filter.get_new_entries()
        for event_log in event_logs:
            bytesHTTPRes = event_log['args']["bytesHTTPRes"]
            actualHTTPRes = pickle.loads(bytesHTTPRes)
            return HttpResponse(content=actualHTTPRes.content, status=actualHTTPRes.status_code, content_type=actualHTTPRes.headers.get('Content-Type'))

  

