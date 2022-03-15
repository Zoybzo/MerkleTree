import random

from _MerkleTree import *

if __name__ == '__main__':
    # 数据生成: 随机生成 128 个节点
    size = 128
    data = random.sample(range(1, 1000), size)
    merkleTree = MerkleTree(data)
    merkleTree.build_tree()
    path = merkleTree.get_merkle_path(15)
    print(path)
    check_result, bad_node = merkleTree.check_merkle_path(path, 11)
    print(check_result, bad_node)
