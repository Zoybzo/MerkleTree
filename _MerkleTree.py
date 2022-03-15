import queue
from hashlib import sha256
from graphviz import Digraph

# Computer A sends a hash of the file to computer B.
# Computer B checks that hash against the root of the Merkle tree.
# If there is no difference, we're done! Otherwise, go to step 4.
# If there is a difference in a single hash, computer B will request the roots of the two subtrees of that hash.
# Computer A creates the necessary hashes and sends them back to computer B.
# Repeat steps 4 and 5 until you've found the data blocks(s) that are inconsistent.
# It's possible to find more than one data block that is wrong because there might be more than one error in the data.


LEAF = 'LEAF'
INNER = 'INNER'
L = 'L'
R = 'R'


class Node:
    def __init__(self, node_val, node_type=INNER):
        self.val = node_val
        self.type = node_type
        self.left = None
        self.right = None
        self.parent = None
        self.sibling = None
        self.position = ''


def get_hash(s1, s2=''):
    return sha256((s1 + s2).encode()).hexdigest()


class MerkleTree:
    def __init__(self, data):
        """

        :param data: 排序后的数据
        """
        self.root = None
        self.leaves = [Node(get_hash(str(leaf)), LEAF) for leaf in data]

    def build_tree(self):
        q = queue.Queue()
        for node in self.leaves:
            q.put(node)
        while not q.empty():
            left = q.get()
            if q.empty():
                self.root = left
                break
            right = q.get()
            parent = Node(get_hash(left.val, right.val))
            left.parent, right.parent = parent, parent
            left.sibling, right.sibling = right, left
            left.position, right.position = L, R
            parent.left, parent.right = left, right
            q.put(parent)
        return self.root

    def get_merkle_path(self, index_of_node):
        if index_of_node >= len(self.leaves):
            raise IndexError
        if self.root is None:
            raise Exception('Root is None.')
        now_node = self.leaves[index_of_node]
        path = []
        while now_node.sibling is not None:
            path.append(now_node.sibling.val)
            now_node = now_node.parent
        return path

    def check_merkle_path(self, paths, index_of_node):
        if index_of_node >= len(self.leaves):
            raise IndexError
        if self.root is None:
            raise Exception('Root is None.')
        now_node = self.leaves[index_of_node]
        check = True
        node = None
        for path_val in paths:
            if now_node.position == 'L':
                val = get_hash(now_node.val, path_val)
            else:
                val = get_hash(path_val, now_node.val)
            if val != now_node.parent.val:
                check, node = False, now_node.parent.val
                break
            now_node = now_node.parent
        return [check and now_node == self.root, node]
