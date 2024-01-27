class Node:
    """
    Node class for use in MerkleTree class

    Args:
        left (Node): Left child
        right (Node): Right child
        transaction (str): transaction string, idk if relevant, just for completeness
        hashed_value (str): Hashed value of node
    """
    def __init__(self, left, right, transaction, hashed_value) -> None:
        self.left = left
        self.right = right
        self.transaction = transaction
        self.hashed_value = hashed_value

    def hash(self, value):
        """
        Hashes a value

        Args:
            value (str): value to be hashed

        Returns:
            str: hashed value
        """
        # return someHashFunction(value)
        return hash(value) #Standard hash function in python, didnt read up on what exact function to use

class MerkleTree:
    """
    Builds a merkle tree and makes it accessible through `get_root()`

    Args:
        txs (list[str]): list of transactions
    """
    def __init__(self, txs):
        self.data = None #What is this supposed to be?
        self.leaf_nodes = txs
        self.build_tree()

    def build_tree(self):
        """
        Recursively build a Merkle tree.\n

        """
        leaves: list[Node] = [Node(None, None, transaction, Node.hash(transaction)) for transaction in self.leaf_nodes]
        self.root = recursion(leaves)
        def recursion(nodes):
            middle = len(nodes)//2 #Always keeps the even number on the left
            if len(nodes) == 2:
                f"{nodes[0].transaction}+{nodes[1].transaction}"
                hashed_value = Node.hash(nodes[0].hashed_value + nodes[1].hashed_value)
                return Node(nodes[0], nodes[1], transaction, hashed_value)
            try: #Deal with uneven number of leaves. Possible to add dummy node instead probably
                left = recursion(nodes[:middle])
                right = recursion(nodes[middle:])
                transaction = f"{left.transaction}+{right.transaction}"
                hashed_value = Node.hash(left.hashed_value + right.hashed_value)
            except: #listIndexOutOfRange?
                left = recursion(nodes[0])
                right = None
                transaction = f"{left.transaction}"
                hashed_value = Node.hash(left.hashed_value)

            # return Node(left, right, transaction, hashed_value)

    def get_root(self):
        # return self.root #Brain fried, not sure
        raise NotImplementedError("Not sure what to do here :(")
