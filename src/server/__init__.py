from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.parent

DIFFICULTY = 7
USER_PATH = PROJECT_PATH / "vis" / "users"
USER_FILE = "users.db"
BLOCKCHAIN_PATH = PROJECT_PATH / "vis" / "blockchain"
BLOCKCHAIN_FILE = "blockchain.pkl"
KEY_PAIRS_PATH = PROJECT_PATH / "vis" / "users"

# network
PORT = '8080'
ADDRESS = 'ete011@inf3203.cs.uit.no'
URL = 'https://' + ADDRESS + ':' + PORT + '/'

SELF = 'ble015'

# endpoints
BLOCK_PROPOSAL = 'block_proposal'
GET_BLOCKCHAIN = 'get_blockchain'
GET_USERS = 'get_users'
REQUEST_TXS = 'request_txs'
GET_DATABASE = 'get_database'
REQUEST_DIFFICULTY = 'request_difficulty'