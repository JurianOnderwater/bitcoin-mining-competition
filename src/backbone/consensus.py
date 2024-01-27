# backbone/consensus.py
from merkle import MerkleTree
from hashlib import sha256


# TODO: Implement Proof of Work
class PoW:
    def __init__(self) -> None:
        self.proof()

    def double_hash(value):
        if type(value) == str:
            return sha256(sha256(value))
        elif type(value) == list[str]:
            return sha256(sha256(str(''.join(value))))

    def block_header(self, prev, timestamp, merkle):
        return ''.join([str(prev), str(timestamp), str(merkle)])

    def proof(self):
        NONCE = 0
        while not IS_VALID(result):
            result = self.double_hash([self.block_header(ATTRIBUTES), NONCE])
            NONCE += 1
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

