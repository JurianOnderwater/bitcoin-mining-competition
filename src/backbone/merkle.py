# TODO: Make Merkle tree structure

class MerkleTree:
    def __init__(self, txs):
        self.data = None
        self.leaf_nodes = txs
        self.build_tree()

    def build_tree(self):
        # hash here already or just build tree and build in POW
        return None

    def get_root(self):
        return None
