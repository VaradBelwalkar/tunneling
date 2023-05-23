from web3 import Web3
from web3.auto import w3
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import pickle
import json
from dotenv import load_dotenv,find_dotenv
from web3.middleware import geth_poa_middleware
import random
from eth_account import Account

#dotenv_path = join(dirname(__file__), '.env')
load_dotenv(find_dotenv())

infura_key = os.environ.get("INFURA_KEY")
private_key_hex = os.environ.get("PRIVATE_KEY_HEX")
contract_address = os.environ.get("CONTRACT_ADDRESS")
#print(infura_key,private_key_hex,contract_address)
#infura_key = "52d0c9535433469cbfdf69f11c11052a"
#private_key_hex = "75a69d179ae87b2cdb17dbff6668961f2ea7f6bdb275b1b831b4b978c7cdf0df"
#contract_address  = "0xF2238D43168DDa8eFec3Cd30cEc3Ae2a748B22D4"
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
				"indexed": False,
				"internalType": "string",
				"name": "context",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "bytes",
				"name": "bytesHTTPReq",
				"type": "bytes"
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
				"name": "context",
				"type": "string"
			},
			{
				"indexed": False,
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


account = w3.eth.account.from_key(private_key_hex)


def serialize_http_request(http_request):
    serialized_request = {
        'method': http_request.method,
        'path': http_request.path,
        'headers': dict(http_request.headers),
        'body': http_request.body.decode('utf-8')
    }
    return pickle.dumps(serialized_request)



def createUniqueContext():
    return str(random.randint(1,10000))


# Define function to listen to event and process arguments
@csrf_exempt
def forward_to_contract(HTTPReq,path):
  #Pickle the copy of request object without nested object which is of io.BufferReader type
  #jsonHTTPReq = json.dumps(HTTPReq)
  bytesHTTPReq = serialize_http_request(HTTPReq)
  port = HTTPReq.META.get('SERVER_PORT')
  print("The port used to access this server is: {port}")
  context = createUniqueContext()
  event_filter = contract.events.get_response.create_filter(fromBlock='latest',argument_filters={'context':context})
  tx_hash = contract.functions.request_handler(context,bytesHTTPReq).build_transaction({
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

  

