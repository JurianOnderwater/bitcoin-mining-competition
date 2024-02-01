# backbone/consensus.py
from abstractions.block import Block
from server import DIFFICULTY, USER_PATH, SELF
import rsa
from utils.cryptographic import load_private, load_public, double_hash, verify_signature
import multiprocessing as mp
from multiprocessing import Pool

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
        with open(f"{USER_PATH}{SELF}_pvk.pem", "r") as keyfile:
            key = load_private(keyfile.read())
            return rsa.sign(b_msg, key, 'SHA-1')

    def is_valid(self, value):
        return value[:DIFFICULTY] == '0' * DIFFICULTY

    def block_header(self) -> str:
        return f'{str(self.block.prev)}{str(self.block.time)}{str(self.block.merkle_root)}'
    
    def find_valid_hash(self, nonce):
        print(f'nonce: {nonce}, cpu: {mp.current_process().name}')
        header = self.header
        while True:
            hash_input = f'{header}{str(nonce)}'
            result = double_hash(hash_input)
            if self.is_valid(result):
                print(f"{mp.current_process().name} found valid hash: {result}")
                return result, nonce
            nonce += 1

    def proof(self):
        block_header = self.block_header()
        self.header = block_header
        nonces = [2**32 // mp.cpu_count() * x for x in range(mp.cpu_count())]
        
        # multiprocess to find valid hash
        with Pool() as pool:
            for result in pool.imap_unordered(self.find_valid_hash, nonces):
                if self.is_valid(result[0]):
                    self.block.hash, self.block.nonce = result
                    pool.terminate()
                    break

        # sign hash and verify signature
        self.block.signature = self.sign(self.block.hash)
        with open(f"{USER_PATH}{SELF}_pbk.pem", "r") as keyfile:
            pubkey = load_public(keyfile.read())
            verify_signature(self.block.hash, self.block.signature, pubkey)

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
