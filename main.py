import random

from _MerkleTree import *

my_size = 8
target_node = 4
error_node = 4
Test_exist = True
Test1 = False

none_node = 4.5


def output(node):
    print('-----------------------------TEST-------------------------------------')
    print('Tree Level Order:', tree_level_order)
    print('Tree Level Order Mapping:', tree_level_order_fake_val)
    print('Merkle Path for %d:'.format(node), path)
    print('Merkle Path Mapping for %d:'.format(node), path_fake_val)
    print('Use Path to Check:', path_check)
    print('Test Passed:', check_result)
    print('Error:', bad_node)
    print('Error Mapping:', bad_node_fake_val)
    merkleTree.display()  # Yellow is path_node, Green is witness, Red is target_node
    print('---------------------------TEST_OVER-----------------------------------')


if __name__ == '__main__':
    # 数据生成: 随机生成 my_size 个节点
    size = my_size
    data = random.sample(range(1, 1000), size)
    merkleTree = MerkleTree(data)
    merkleTree.build_tree()
    tree_level_order, tree_level_order_fake_val = merkleTree.get_level_order()

    if Test_exist:
        path, path_fake_val = merkleTree.get_merkle_path(target_node)
        if Test1:
            path_check = path
            check_result, bad_node, bad_node_fake_val = merkleTree.check_merkle_path(path_check, error_node)
        else:
            path_check = [5, 10, 12]
            check_result, bad_node, bad_node_fake_val = merkleTree.check_merkle_path(path_check, error_node,
                                                                                     USE_HASH=False)
        output(target_node)
    else:
        path, path_fake_val = merkleTree.get_merkle_path(none_node)
        path_check = [5, 10, 12]
        check_result, bad_node, bad_node_fake_val = merkleTree.check_merkle_path(path_check, error_node,
                                                                                 USE_HASH=False)
        output(none_node)
