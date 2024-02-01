"""
Enrico Tedeschi @ UiT - Norges Arktiske Universitet, Faculty of Computer Science.
enrico.tedeschi@uit.no

INF 3203 - Advanced Distributed Systems

Assignment 1 - Blockchain Mining Competition

Usage:
        -h                  : display usage information
        -i [b, u]           : display information for blocks or users   #TODO
        -t                  : request N transactions                    #TODO
        -m                  : mine a block                              #TODO
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

from backbone.consensus import PoW
from abstractions.block import Block
from abstractions.transaction import Transaction

from utils.flask_utils import flask_call
from abstractions.block import Blockchain
import server
from utils.view import visualize_blockchain, visualize_blockchain_terminal
from time import perf_counter


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:tmdv:")
        # print(f'opts : {opts}\nargs : {args}')
        valid_args = False
        for opt, arg in opts:
            if opt == "-h":  # usage
                print(__doc__)
                valid_args = True
                break
            if opt == "-m":  # mine block
                while True:
                    _, transactions, _ = flask_call("GET", server.REQUEST_TXS)
                    _, blockchain, _ = flask_call("GET", server.GET_BLOCKCHAIN)
                    previous_block = blockchain["chain"][-1]
                    valid_args = True
                    block = Block(
                        hash=None,  # Needs to be found
                        nonce=0,
                        time=datetime.now().timestamp(),
                        creation_time=0,
                        height=previous_block["height"] + 1,
                        previous_block=previous_block["hash"],  # GET from server
                        transactions=[Transaction.load_json(json.dumps(t)) for t in transactions], 
                        main_chain=True,
                        confirmed=False,
                        mined_by=server.SELF,  # Us
                        signature=None,
                    )  # Done in consensus.py
                    start = perf_counter()
                    block = PoW(block).proof()
                    block.creation_time = perf_counter() - start
                    response, _, _ = flask_call("POST", server.BLOCK_PROPOSAL, data=block.to_dict())
                    print(response)
                    if args[0] == "c":
                        continue
                    else:
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


def connect_to_server():
    """

    :return:
    """
    response = requests.get(server.URL, verify=False)
    return response


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main(sys.argv[1:])
