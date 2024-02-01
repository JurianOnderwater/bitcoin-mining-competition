# backbone/consensus.py
from abstractions.block import Block
from hashlib import sha256
from server import DIFFICULTY, USER_PATH, SELF
import rsa
from utils.cryptographic import load_private, double_hash

class PoW:
    def __init__(self, block: Block) -> None:
        self.block = block

    def sign(self, message):
        """
        sign with private key
        :param message:
        :return:
        """
        b_msg = bytes(message, 'utf-8')
        with open(USER_PATH / f"{SELF}_pvk.pem", "r") as keyfile:
            key = load_private(keyfile.read())
            return rsa.sign(b_msg, key, 'SHA-1')

    def is_valid(self, value):
        return value[:DIFFICULTY] == '0' * DIFFICULTY

    def block_header(self) -> str:
        return f'{str(self.block.prev)}{str(self.block.time)}{str(self.block.merkle_root)}'

    def proof(self):
        NONCE = self.block.nonce
        block_header = self.block_header()
        while True:
            result = double_hash(block_header + str(NONCE))
            if self.is_valid(result):
                break
            NONCE += 1
        self.block.hash = result
        self.block.signature = self.sign(self.block.hash)
        return self.block
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
