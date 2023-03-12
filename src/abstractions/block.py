# abstractions/block.py

from backbone.merkle import MerkleTree
from abstractions.transaction import Transaction
from utils.view import visualize_blockchain
from utils.cryptographic import double_hash, save_signature, load_signature
import json

class Block:
    """
    Dummy Bitcoin Block
    """
    def __init__(self, hash, nonce, time, creation_time, previous_block=None, transactions=None, main_chain=True,
                 confirmed=False, merkle_root=None, next=[], mined_by=None, signature=None):
        if transactions is None:
            transactions = []
        self.transactions = transactions
        self.hash = hash
        self.prev = previous_block  # hash of the previous block
        self.nonce = nonce
        self.time = time # datetime.now().timestamp()
        self.creation_time = creation_time
        self.merkle_tree = self.create_merkle_tree()
        if merkle_root is None:
            self.merkle_root = self.merkle_tree.get_root()['hash']
        else:
            self.merkle_root = merkle_root
        self.main_chain = main_chain  # if False, block is in a forked branch
        self.confirmed = confirmed  # becomes True if main_chain and more than N_BLOCKS_PER_BRANCH
        self.next = next
        self.mined_by = mined_by  # dictionary for block verification. {username : priv_k(self.hash)}
        self.signature = signature  # signature with miner private key of block hash

    def to_dict(self):
        """
        make Blocks into dict for serialization
        :return:
        """
        signature = save_signature(self.signature)
        return {
            "transactions": [t.to_dict() for t in self.transactions],
            "hash": self.hash,
            "prev": self.prev,
            "nonce": self.nonce,
            "time": self.time,
            "creation_time": self.creation_time,
            "merkle_root": self.merkle_root,
            "main_chain": self.main_chain,
            "confirmed": self.confirmed,
            "next": self.next,
            "mined_by": self.mined_by,
            "signature" : signature
        }

    @classmethod
    def load_json(cls, data):
        data = json.loads(data)
        transactions = [Transaction.load_json(json.dumps(t)) for t in data["transactions"]]
        signature = load_signature(data["signature"])
        return cls(
            hash=data['hash'],
            time=data['time'],
            nonce=data['nonce'],
            creation_time=data['creation_time'],
            transactions=transactions,
            previous_block=data['prev'],
            main_chain=data['main_chain'],
            confirmed=data['confirmed'],
            next=data['next'],
            merkle_root=data['merkle_root'],
            mined_by=data['mined_by'],
            signature=signature,
        )

    def create_merkle_tree(self):
        """
        creates a merkle tree from all transactions
        :return: a merkle tree structure
        """
        hashes = []
        for t in self.transactions:
            hashes.append(t.hash)
        m = MerkleTree(hashes)
        return m

    def add_transaction(self, transaction):
        """Add a new transaction to the block"""
        self.transactions.append(transaction)

    def get_transactions(self):
        """Retrieves the transactions in the block"""
        return self.transactions

    def __str__(self):
        """
        redefine builtin func for printing
        :return:
        """
        return str(self.__class__) + ": " + str(self.__dict__)


class Blockchain:
    """
    Blockchain class as a list of blocks
    """
    def __init__(self, block_list):
        self.block_list = block_list
        self.chain = self.make_chain_from_list()
        self.is_valid = self.is_chain_valid()

    def make_chain_from_list(self):
        """
        makes a dictionary from a list of blocks
        :return: dictionary {hash : Block}
        """
        dic = dict()
        for b in self.block_list:
            dic[b.hash] = b
        return dic

    def to_dict(self):
        """
        make Blockchain into dict for serialization
        :return: dictionary of this object instance
        """

        return {
            "block_list" : None,
            "chain" : [b.to_dict() for _, b in self.chain.items()],
            "is_valid" : self.is_valid
        }

    @classmethod
    def load_json(cls, data):
        data = json.loads(data)
        blocks = [Block.load_json(json.dumps(b)) for b in data["chain"]]
        return cls(
            block_list=blocks,
        )

    def is_chain_valid(self):
        """
        verify the current blockchain is valid
        :return:
        """
        for key in self.chain:
            current_b = self.chain[key]
            if current_b.prev == 'None':
                # genesis block shall not be checked
                pass
            else:
                # previous block
                prev_b = self.chain[self.chain[key].prev]
                # calculate current block hash
                data = str(current_b.prev) + str(current_b.time) + str(current_b.merkle_root) + str(current_b.nonce)
                current_b_hash = double_hash(data)
                if current_b.hash != current_b_hash:
                    # current hash is different from the calculated one
                    return False
                if current_b.prev != prev_b.hash:
                    # previous hash saved on the blockchain is different from the one fetched in the block list
                    return False
        return True

    def add_block(self, new_block):
        """
        add a new block
        :param new_block : block just added
        :return: bool
        """
        # if genesis add it to the chain
        if new_block.prev == 'None':
            self.chain[new_block.hash] = new_block
            return True
        else:
            # not genesis
            value = self.chain.get(new_block.prev)
            if value is not None:
                # the previous block exists
                # set main_chain same as predecessor
                new_block.main_chain = self.chain[new_block.prev].main_chain
                # add block to the chain
                self.chain[new_block.hash] = new_block
                # add successors
                self.chain[new_block.prev].next.append(new_block.hash)
                return True
            else:
                return False

    def find_forks(self):
        """
        find all the forked branches in the blockchain
        :return: dictionary {'hash' : <number of blocks pointing at it>}
        """
        prev_hash_dict = dict()
        for k in self.chain:
            p_hash = self.chain[k].prev
            if p_hash in prev_hash_dict:
                prev_hash_dict[p_hash] += 1
            else:
                prev_hash_dict[p_hash] = 1
            return prev_hash_dict

    def visit_branch_update_main_chain(self, hash, value=False):
        """
        recursively traverse the blockchain and update the main_chain value
        :param hash: starting block hash
        :param value
        :return:
        """
        b = self.chain[hash]
        b.main_chain = value
        print(f'Block {hash[:8]} set to {value}')
        for n in b.next:
            self.visit_branch_update_main_chain(n, value)

    def confirm_chain(self):
        """
        when a fork happens, it confirms the longest chain if at
        least one branch is more than N_BLOCKS_PER_BRANCH blocks long
        :return:
        """
        from server import N_BLOCKS_PER_BRANCH
        for k in self.chain:
            b = self.chain[k]
            if not b.confirmed:  # the chain can become false only if block has not being confirmed yet todo: test this if statement
                if len(b.next) > 1:  # if fork
                    hashes = b.next
                    count_branches = []
                    max_value = 0
                    hash = None
                    # count blocks for each branch
                    for h in hashes:
                        c = count_blocks_per_branch(self.chain, h)
                        count_branches.append(c)
                        # get longest branch
                        if c[h] > max_value:
                            max_value = c[h]
                            hash = h
                        elif c[h] == max_value:
                            # branches are equal
                            hash = None
                        else:
                            pass
                    if hash is not None:
                        if max_value > N_BLOCKS_PER_BRANCH:
                            # change main_chain values
                            for c in count_branches:
                                for h, v in zip(c.keys(), c.values()):
                                    if h != hash:
                                        # if is not the main chain
                                        self.visit_branch_update_main_chain(h, False)
                                    else:
                                        # main chain
                                        self.visit_branch_update_main_chain(h, True)


def count_blocks_per_branch(blockchain, start_hash_branch):
    """
    it counts blocks at every branch
    :param blockchain: Blockchain.chain object
    :param start_hash_branch: hash where to start the count
    :return: {hash : <count>}
    """
    count = dict()
    visited = set()
    def dfs(block_hash, branch_id):
        """
        recursive function that implements a depth-first search
        algorithm to traverse the blockchain starting from a given
        block hash. The purpose of the dfs function is to count
        the number of blocks in each branch of the blockchain by visiting
        each block exactly once and adding its count to a dictionary that
        maps each branch to its count. The algorithm uses the depth-first
        approach to traverse the blockchain by visiting the first successor
        of a block before visiting the second, and so on, until there are
        no more successors to visit, then backtracking to visit the next
        unvisited successor if there are any.
        :param block_hash:
        :param branch_id:
        :return:
        """
        nonlocal count
        if block_hash in visited:
            return
        visited.add(block_hash)
        if branch_id not in count:
            count[branch_id] = 0
        count[branch_id] += 1
        # for next_block_id in list of next
        for next_block_id in blockchain[block_hash].next:
            dfs(next_block_id, branch_id)
    dfs(start_hash_branch, start_hash_branch)
    return count
