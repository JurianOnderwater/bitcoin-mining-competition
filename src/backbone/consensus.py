# backbone/consensus.py
from abstractions.block import Block
from merkle import MerkleTree
from hashlib import sha256
from server import DIFFICULTY
import datetime


# TODO: Implement Proof of Work
class PoW:
    def __init__(self, block: Block) -> None:
        self.block = block
        self.proof()

    def is_valid(self, value):
        return value[:DIFFICULTY] == '0' * DIFFICULTY
    
    def double_hash(value):
        if type(value) == str:
            return sha256(sha256(value))
        elif type(value) == list[str]:
            return sha256(sha256(str(''.join(value))))

    def block_header(self):
        return ''.join([str(self.block.time), str(self.block.previous_block), str(self.block.merkle_root())])

    def proof(self):
        NONCE = self.block.nonce
        while not self.is_valid(result):
            result = self.double_hash([self.block_header(), NONCE])
            self.block.nonce += 1
        BROADCAST_TO_NETWORK(result)
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
# TODO: 
    root =  MerkleTree()
    block = Block(hash=None, 
                  nonce=None, 
                  time=datetime.now().timestamp(), 
                  creation_time=datetime.now().timestamp(),
                  height=None, 
                  previous_block=None, 
                  transactions=None, 
                  main_chain=True, 
                  confirmed=False, 
                  next=None, 
                  mined_by=None, 
                  signature=None)

