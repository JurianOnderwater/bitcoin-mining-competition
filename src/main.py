"""
Enrico Tedeschi @ UiT - Norges Arktiske Universitet, Faculty of Computer Science.
enrico.tedeschi@uit.no

INF 3203 - Advanced Distributed Systems

Assignment 1 - Blockchain Mining Competition

Usage:
        -h                  : display usage information
        -i [b, u]           : display information for blocks or users
        -t                  : request N transactions
        -m [pl]             : mine a block, optionally parallel and looping
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
import argparse

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
        parser = construct_parser()
        cmd_input = parser.parse_args(argv)

        # convert to dictionary and parse out unused options
        cmd_input = dict(vars(cmd_input))
        cmd_input = {k: v for k, v in cmd_input.items() if v is not None and v is not False}

        valid_args = False
        for opt, args in cmd_input.items():
            print(f"opt: {opt}, args: {args}")
            if opt == "h":
                print(__doc__)
                valid_args = True

            elif opt == "m":
                while True:
                    block = mine_block(parallelize=("p" in args))
                    response, _, _ = flask_call("POST", server.BLOCK_PROPOSAL, data=block.to_dict())
                    print(response)
                    if not "l" in args:
                        break
                    valid_args = True

            elif opt == "i":
                if "b" in args:
                    response, _, _ = flask_call("GET", server.GET_BLOCKCHAIN)
                    print(response)
                    valid_args = True
                elif "u" in args:
                    response, _, _ = flask_call("GET", server.GET_USERS)
                    print(response)
                    valid_args = True
                else:
                    valid_args = False

            elif opt == "t":
                response, _, _ = flask_call("GET", server.REQUEST_TXS)
                print(response)
                valid_args = True

            elif opt == "v":
                if "b" in args:
                    # fetch blockchain from server
                    # get blockchain info
                    _, blockchain, code = flask_call("GET", server.GET_BLOCKCHAIN)
                    if blockchain:
                        b_chain = Blockchain.load_json(json.dumps(blockchain))
                        # saves the blockchain as pdf in "vis/blockchain/blockchain.pdf"
                        visualize_blockchain(b_chain.block_list, n_blocks=40)
                        visualize_blockchain_terminal(b_chain.block_list, n_blocks=40)
                    valid_args = True

            elif opt == "d":
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

def construct_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Blockchain Mining Competition", add_help=False)
    parser.add_argument("-h", action="store_true", help="display usage information")
    parser.add_argument("-i", nargs=1, choices=["b", "u"], help="display information on blocks or users")
    parser.add_argument("-t", action="store_true", help="request N transactions")
    parser.add_argument("-m", nargs='*', choices=["p", "l"], help="mine a block, optionally parallel and/or looping")
    parser.add_argument("-v", nargs=1, choices=["b"], help="visualize blockchain, saved to vis/blockchain/blockchain.pdf")
    parser.add_argument("-d", action="store_true", help="request DIFFICULTY level")
    return parser

def mine_block(parallelize: bool) -> Block:
    _, transactions, _ = flask_call("GET", server.REQUEST_TXS)
    _, blockchain, _ = flask_call("GET", server.GET_BLOCKCHAIN)
    previous_block = blockchain["chain"][-1]
    prev_block_hash = previous_block["hash"]
    time = datetime.now().timestamp()
    merkle_root = MerkleTree([t["hash"] for t in transactions]).get_root()
    block_header = prev_block_hash + str(time) + str(merkle_root["hash"])
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
