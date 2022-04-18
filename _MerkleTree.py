import math
import queue
from bisect import bisect
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

HASH = 'hash'

NORMAL = 'normal'
TARGET = 'target'
WITNESS = 'witness'
PATH_NODE = 'path_node'
ERROR_NODE = 'error_node'

_color_map = {
    'normal': '#f2e9e4',
    'witness': '#06d6a0',
    'target': '#ef476f',
    'path_node': '#ffd166',
    'error_node': '#073b4c',
}


class Node:
    def __init__(self, node_val, node_type=INNER, identity=NORMAL):
        self.val = node_val
        self.type = node_type
        self.left = None
        self.right = None
        self.parent = None
        self.sibling = None
        self.position = ''
        self.fake_val = None  # for graph
        self.identity = identity  # for color


def get_hash(s1, s2=''):
    return sha256((s1 + s2).encode()).hexdigest()


class MerkleTree:
    def __init__(self, data, color_map=None):
        """

        :param data: 排序后的数据
        """
        if color_map is None:
            color_map = _color_map
        self.root = None
        self.leaves = [Node(get_hash(str(leaf)), LEAF, NORMAL) for leaf in data]
        for i in range(0, len(self.leaves)):
            self.leaves[i].fake_val = i
        # self.leaves.fake_val = [i for i in range(0, len(self.leaves))]
        self.fake_cnt = len(self.leaves)
        self.color_map = color_map
        self.level_order = []
        self.level_order_fake_val = []
        self.proof_index = None
        self.nodes = self.leaves

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
            parent.left, parent.right, parent.fake_val = left, right, self.fake_cnt
            self.fake_cnt += 1
            self.nodes.append(parent)
            q.put(parent)
        return self.root

    def get_level_order(self):
        if len(self.level_order):
            return self.level_order, self.level_order_fake_val
        q = queue.Queue()
        q.put(self.root)
        while not q.empty():
            times = q.qsize()
            for i in range(0, times):
                now = q.get()
                if now is None:
                    continue
                self.level_order.append(now.val)
                self.level_order_fake_val.append(now.fake_val)
                q.put(now.left), q.put(now.right)
        return self.level_order, self.level_order_fake_val

    def re_dyeing(self, error_node=False):
        q = queue.Queue()
        q.put(self.root)
        while not q.empty():
            now = q.get()
            if now is None:
                continue
            if error_node:
                if now.identity is ERROR_NODE:
                    now.identity = NORMAL
            else:
                now.identity = NORMAL
            q.put(now.left), q.put(now.right)

    def get_merkle_path(self, index_of_node):
        if index_of_node % 1 != 0:
            # 证明一个节点不存在
            return self._get_merkle_path(index_of_node)
        if index_of_node >= len(self.leaves):
            raise IndexError
        if self.root is None:
            raise Exception('Root is None.')
        self.re_dyeing()
        self.proof_index = index_of_node
        now_node = self.leaves[index_of_node]
        now_node.identity = TARGET
        path, path_fake_val = [], []
        while now_node.sibling is not None:
            path.append(now_node.sibling.val)
            path_fake_val.append(now_node.sibling.fake_val)
            # color
            now_node.sibling.identity = WITNESS
            if now_node.parent is not None:
                now_node.parent.identity = PATH_NODE
            # color over
            now_node = now_node.parent
        return path, path_fake_val

    def _binary_search(self, l_node, r_node, x):
        """
        后续对对象数组进行二分查找可能会使用，如果找到了调库的方法可以在比较效率后有选择地使用
        :param l_node:
        :param r_node:
        :param x:
        :return:
        """
        while l_node <= r_node:
            mid = (l_node + r_node) >> 1
            if mid > x:
                l_node = mid + 1
            elif mid < x:
                r_node = mid
        return l_node

    def _get_merkle_path(self, index_of_node):
        # index_l = self._binary_search(0, len(self.leaves), index_of_node)
        index_l = math.floor(index_of_node)
        index_r = math.ceil(index_of_node)
        l_path, l_path_fake_val = self.get_merkle_path(index_l)
        r_path, r_path_fake_val = self.get_merkle_path(index_r) if index_r < len(self.leaves) else [], []
        return [l_path, r_path], [l_path_fake_val, r_path_fake_val]

    def check_merkle_path(self, paths, index_of_node, USE_HASH=True):
        if index_of_node >= len(self.leaves):
            raise IndexError
        if self.root is None:
            raise Exception('Root is None.')
        self.re_dyeing(error_node=True)
        now_node = self.leaves[index_of_node]
        if self.proof_index != index_of_node:
            now_node.identity = ERROR_NODE
            return False, now_node.val, now_node.fake_val
        check, node, node_fake_val = True, None, None
        for path_val in paths:
            if now_node.position == 'L':
                val = get_hash(now_node.val, path_val if USE_HASH else self.nodes[path_val].val)
            else:
                val = get_hash(path_val if USE_HASH else self.nodes[path_val].val, now_node.val)
            if val != now_node.parent.val:
                now_node.parent.identity = ERROR_NODE
                check, node, node_fake_val = False, now_node.parent.val, now_node.parent.fake_val
                break
            now_node = now_node.parent
        return check and now_node == self.root, node, node_fake_val

    def display(self):
        dot = Digraph(name='MerkleTree', format='png')
        node = self.root
        q = queue.Queue()
        q.put(node)
        while not q.empty():
            child = q.get()
            if child is None:
                continue
            dot.node(str(child.fake_val), str(child.fake_val), fillcolor=self.color_map[child.identity], style='filled')
            if child.parent is not None:
                dot.edge(str(child.parent.fake_val), str(child.fake_val))
            q.put(child.left), q.put(child.right)
        dot.render(directory='result', view=True)
        return dot



