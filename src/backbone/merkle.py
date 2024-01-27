class Node:
    def __init__(self, left, right, transaction, hashed_value) -> None:
        self.left = left
        self.right = right
        self.transaction = transaction
        self.hashed_value = hashed_value

    def hash(self, value):
        # return someHashFunction(value)
        return hash(value) #Standard hash function in python, didnt read up on what exact function to use

class MerkleTree:
    def __init__(self, txs):
        self.data = None
        self.leaf_nodes = txs
        self.build_tree()

    def build_tree(self):
        # hash here already or just build tree and build in POW?
        leaves: list[Node] = [Node(None, None, transaction, Node.hash(transaction)) for transaction in self.leaf_nodes]
        self.root = recursion(leaves) #Pretty sure this just builds the root,
        def recursion(nodes):
            middle = len(nodes)//2
            if len(nodes) == 2:
                f"{nodes[0].transaction}+{nodes[1].transaction}"
                hashed_value = Node.hash(nodes[0].hashed_value + nodes[1].hashed_value)
                return Node(nodes[0], nodes[1], transaction, hashed_value)
        
            left = recursion(nodes[:middle])
            right = recursion(nodes[middle:])
            transaction = f"{left.transaction}+{right.transaction}"
            hashed_value = Node.hash(left.hashed_value + right.hashed_value)
            return Node(left, right, transaction, hashed_value)

    def get_root(self):
        # return self.root #Brain fried, not sure
        raise NotImplementedError("Not sure what to do here :(")
