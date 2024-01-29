# backbone/consensus.py
from abstractions.block import Block
from merkle import MerkleTree
from hashlib import sha256
from server import DIFFICULTY


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

    def block_header(self, merkle: MerkleTree):
        return ''.join([str(self.block.time), str(self.block.previous_block), str(merkle.get_root())])

    def proof(self):
        NONCE = self.block.nonce
        while not self.is_valid(result):
            result = self.double_hash([self.block_header(merkle=self.block.merkle_root), NONCE])
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
# TODO: Build a block

