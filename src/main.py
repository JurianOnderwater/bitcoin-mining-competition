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

import requests
import json
from datetime import datetime
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import argparse

from backbone.consensus import proof_of_work, sign, mp_proof_of_work
from backbone.merkle import MerkleTree
from abstractions.block import Block, Blockchain
from abstractions.transaction import Transaction

from utils.flask_utils import flask_call
from utils.view import visualize_blockchain, visualize_blockchain_terminal
import server


def main():
    parser = construct_parser()
    args = parser.parse_args()
    if args.i is not None:
        if "b" in args.i:
            response, _, _ = flask_call("GET", server.GET_BLOCKCHAIN)
            print(response)
        elif "u" in args.i:
            response, _, _ = flask_call("GET", server.GET_USERS)
            print(response)
    elif args.t:
        response, _, _ = flask_call("GET", server.REQUEST_TXS)
        print(response)
    elif args.m is not None:
        while True:
            block = mine_block(parallelize=("p" in args.m))
            response, _, _ = flask_call(
                "POST", server.BLOCK_PROPOSAL, data=block.to_dict()
            )
            print(response)
            if "l" not in args.m:
                break
    elif args.v is not None:
        _, blockchain, code = flask_call("GET", server.GET_BLOCKCHAIN)
        if blockchain:
            b_chain = Blockchain.load_json(json.dumps(blockchain))
            # saves the blockchain as pdf in "vis/blockchain/blockchain.pdf"
            visualize_blockchain(b_chain.block_list, n_blocks=40)
            visualize_blockchain_terminal(b_chain.block_list, n_blocks=40)
    elif args.d:
        response, table, code = flask_call("GET", server.REQUEST_DIFFICULTY)
        print(response)
        print(table)
    return 0


def construct_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Blockchain Mining Competition")
    parser.add_argument(
        "-i", nargs=1, choices=["b", "u"], help="display information on blocks or users"
    )
    parser.add_argument("-t", action="store_true", help="request N transactions")
    parser.add_argument(
        "-m",
        nargs="*",
        choices=["p", "l"],
        help="mine a block, optionally parallel and/or looping",
    )
    parser.add_argument(
        "-v",
        nargs=1,
        choices=["b"],
        help="visualize blockchain, saved to vis/blockchain/blockchain.pdf",
    )
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
    disable_warnings(InsecureRequestWarning)
    raise SystemExit(main())
