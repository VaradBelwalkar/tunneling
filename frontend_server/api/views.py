from web3 import Web3
from web3.auto import w3
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import pickle
import json
from dotenv import load_dotenv,find_dotenv
from web3.middleware import geth_poa_middleware
import random
from eth_account import Account

#dotenv_path = join(dirname(__file__), '.env')
load_dotenv(find_dotenv())
config_file = open("config.json")
config_json = json.load(config_file)
infura_key = os.environ.get("INFURA_KEY")
private_key_hex = os.environ.get("PRIVATE_KEY_HEX")
contract_address = os.environ.get("CONTRACT_ADDRESS")
# Set up Web3 connection
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/"+infura_key)) # Replace with your own RPC endpoint

# Set up contract instance and event filter
# Replace with your own contract ABI
contract_abi = config_json["contract_abi"]
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
#remove csrf checking policy for this function
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

  

