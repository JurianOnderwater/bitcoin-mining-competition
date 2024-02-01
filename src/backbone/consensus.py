# backbone/consensus.py
from server import DIFFICULTY, USER_PATH, SELF
import rsa
from utils.cryptographic import load_private, double_hash
from time import perf_counter

"""
+----------------+
|  Block Header  | <--- Previous Block Hash + Timestamp + Merkle Root
+----------------+
        |
        |        +---------------+       +-------------+       +-------------------+
        + ------>|  Double Hash  |------>|  is valid?  |--YES->|  reward 6.25 BTC  |
        |        +---------------+       +-------------+       +-------------------+
        |                                       |
+----------------+                              |
|     Nonce      |<------------ +1 ------------ NO
+----------------+

"""

def sign(message: str):
    """
    sign with private key
    :param message:
    :return:
    """
    with open(f"{USER_PATH}{SELF}_pvk.pem", "r") as keyfile:
        key = load_private(keyfile.read())
        return rsa.sign(message.encode("utf-8"), key, 'SHA-1')

def valid_hash(hash: str):
    return hash[:DIFFICULTY] == '0' * DIFFICULTY

def proof_of_work(block_header: str) -> tuple[str, int, float]:
    """Run consensus for block

    Args:
        block_header (str): Previous Block Hash + Timestamp + Merkle Root

    Returns:
        tuple[str, int]: hash, nonce, perf time
    """
    nonce = 0
    result = ""
    start = perf_counter()
    while not valid_hash(result):
        result = double_hash(block_header + str(nonce))
        nonce += 1
    return result, nonce, perf_counter() - start