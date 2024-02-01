"""
Enrico Tedeschi @ UiT - Norges Arktiske Universitet, Faculty of Computer Science.
enrico.tedeschi@uit.no

INF 3203 - Advanced Distributed Systems

Assignment 1 - Blockchain Mining Competition

Usage:
        -h                  : display usage information
        -i [b, u]           : display information for blocks or users
        -t                  : request N transactions
        -m [pc]             : mine a block, optionally parallel and looping
        -v b                : visualize blockchain, saved to vis/blockchain/blockchain.pdf
        -d                  : request DIFFICULTY level
"""
__author__ = "Enrico Tedeschi"
__copyright__ = "Copyright (C) 2023 Enrico Tedeschi"
__license__ = "GNU General Public License."
__version__ = "v1.0"

import sys
import getopt
import random
import requests
import json
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from backbone.consensus import proof_of_work, sign, mp_proof_of_work
from backbone.merkle import MerkleTree
from abstractions.block import Block
from abstractions.transaction import Transaction

from utils.flask_utils import flask_call
from abstractions.block import Blockchain
import server
from utils.view import visualize_blockchain, visualize_blockchain_terminal


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "him:tdv:")
        # print(f'opts : {opts}\nargs : {args}')
        valid_args = False
        for opt, arg in opts:
            if opt == "-h":  # usage
                print(__doc__)
                valid_args = True
                break
            if opt == "-m":  # mine block
                while True:
                    block = mine_block(parallelize=("p" in arg))
                    response, _, _ = flask_call("POST", server.BLOCK_PROPOSAL, data=block.to_dict())
                    print(response)
                    if not "c" in arg:
                        break
                valid_args = True
            if opt == "-i":
                # INFO
                if arg == "b":
                    response, _, _ = flask_call("GET", server.GET_BLOCKCHAIN)
                    print(response)
                    valid_args = True
                elif arg == "u":
                    response, _, _ = flask_call("GET", server.GET_USERS)
                    print(response)
                    valid_args = True
                else:
                    valid_args = False
            if opt == "-t":
                response, _, _ = flask_call("GET", server.REQUEST_TXS)
                print(response)
                valid_args = True
            if opt == "-v":
                if arg == "b":
                    # fetch blockchain from server
                    # get blockchain info
                    _, blockchain, code = flask_call("GET", server.GET_BLOCKCHAIN)
                    if blockchain:
                        b_chain = Blockchain.load_json(json.dumps(blockchain))
                        # saves the blockchain as pdf in "vis/blockchain/blockchain.pdf"
                        visualize_blockchain(b_chain.block_list, n_blocks=40)
                        visualize_blockchain_terminal(b_chain.block_list, n_blocks=40)
                    valid_args = True
            if opt == "-d":
                response, table, code = flask_call("GET", server.REQUEST_DIFFICULTY)
                print(response)
                print(table)
                valid_args = True
        if valid_args is False:
            print(__doc__)
    except getopt.GetoptError:
        print(__doc__)
        sys.exit(2)
    except ValueError as e:
        print(e)
        print(__doc__)
        sys.exit(2)  # exit due to misuse of shell/bash --> check documentation
    except KeyboardInterrupt as e:
        print(e)


def mine_block(parallelize: bool) -> Block:
    _, transactions, _ = flask_call("GET", server.REQUEST_TXS)
    _, blockchain, _ = flask_call("GET", server.GET_BLOCKCHAIN)
    previous_block = blockchain["chain"][-1]
    prev_block_hash = previous_block["hash"]
    time = datetime.now().timestamp()
    merkle_root = MerkleTree([t["hash"] for t in transactions]).get_root()
    block_header = prev_block_hash + str(time) + str(merkle_root)
    if parallelize:
        block_hash, nonce, perf_time = mp_proof_of_work(block_header)
    else:
        block_hash, nonce, perf_time = proof_of_work(block_header)
    signature = sign(block_hash)

    block = Block(
        hash=block_hash,
        nonce=nonce,
        time=time,
        creation_time=perf_time,
        height=previous_block["height"] + 1,
        previous_block=prev_block_hash,
        transactions=[Transaction.load_json(json.dumps(t)) for t in transactions], 
        mined_by=server.SELF,
        signature=signature,
    )
    return block

def connect_to_server():
    """

    :return:
    """
    response = requests.get(server.URL, verify=False)
    return response


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main(sys.argv[1:])
