from hashlib import sha256
import unittest



class MerkleTree:
    """
    Builds a merkle tree and makes it accessible through `get_root()`

    Args:
        tx_hashes (list[str]): list of transaction hashes
    """
    def __init__(self, tx_hashes: str):
        self.data = None #What is this supposed to be?
        self.tx_hashes = tx_hashes
        self.root = self.build_tree()

    def build_tree(self):
        """
        Recursively build a Merkle tree.

        """
        hashed = [self.hash(t) for t in self.tx_hashes]
        while True:
            hashed = [
                self.hash(hashed[i] + hashed[i+1]) if i+1 < len(hashed) else self.hash(hashed[i] +  hashed[i]) 
                for i in range(0, len(hashed), 2)
                ]
            if len(hashed) == 1:
                break
        return hashed[0]

    def get_root(self):
        return {'hash': self.root}
    
    @staticmethod
    def hash(tx: str) -> str:
        return sha256(tx.encode('utf-8')).hexdigest()


class TestMerkleTree(unittest.TestCase):
    def test_algo(self):
        m = MerkleTree(["tx0", "tx1", "tx2", "tx3"])
        tx0 = MerkleTree.hash("tx0")
        tx1 = MerkleTree.hash("tx1")
        tx2 = MerkleTree.hash("tx2")
        tx3 = MerkleTree.hash("tx3")
        tx00 = MerkleTree.hash(tx0+ tx1)
        tx01 = MerkleTree.hash(tx2+ tx3)
        root = MerkleTree.hash(tx00+ tx01)
        print(root)
        print(m.get_root())
        assert root == m.get_root()['hash']
    
    def test_uneven(self):
        m = MerkleTree(["tx0", "tx1", "tx2", "tx3", "tx4"])
    def test_even(self):
        m = MerkleTree(["tx0", "tx1", "tx2", "tx3"])
