import AGCT_tree

def test_create_tree_structure(fresh_tree):
    root = fresh_tree(2)
    # level 0 is not leaf
    assert root.is_leaf is False
    # has all 4 branches
    assert all([root.a_branch, root.c_branch, root.t_branch, root.g_branch])
    # children at level 1 should have children (since height is 2)
    assert root.a_branch.level == 1
    assert root.a_branch.is_leaf is False
    # grandchildren at level 2 should be leaves
    assert root.a_branch.a_branch.level == 2
    assert root.a_branch.a_branch.is_leaf is True

def test_create_tree_structure_0_height(fresh_tree):
    root = fresh_tree(0)
    # level 0 is leaf
    assert root.is_leaf is True
    # should not have any branches
    assert all([root.a_branch is None, root.c_branch is None, root.t_branch is None, root.g_branch is None])

def test_create_positions(fresh_tree):
    tree = fresh_tree(3)
    segment = "ACGT"
    position = 5
    tree.create_positions(segment, position)
    
    node = tree.a_branch.c_branch.g_branch
    assert position in node.positions

def test_create_positions_partial(fresh_tree):
    tree = fresh_tree(3)
    segment = "A"
    position = 10
    tree.create_positions(segment, position)
    
    node = tree.a_branch
    assert position in node.positions
    node = tree.a_branch.c_branch
    assert position not in node.positions

def test_create_positions_empty_string(fresh_tree):
    tree = fresh_tree(2)
    segment = ""
    position = 0
    tree.create_positions(segment, position)
    
    # No positions should be added
    def check_no_positions(node):
        assert len(node.positions) == 0
        for child in [node.a_branch, node.c_branch, node.t_branch, node.g_branch]:
            if child:
                check_no_positions(child)
    
    check_no_positions(tree)

def test_find_factor(fresh_tree):
    tree = fresh_tree(3)
    segments = [("ACG", 0), ("CGT", 1), ("GTA", 2)]
    for seg, pos in segments:
        tree.create_positions(seg, pos)
    
    result = AGCT_tree.find_factor("CGT", tree)
    assert result[0] == [1]
    assert result[1] == 3

def test_find_factor_not_found(fresh_tree):
    tree = fresh_tree(2)
    tree.create_positions("AC", 0)
    
    result = AGCT_tree.find_factor("GT", tree)
    assert result[0] is None
    assert result[1] == None
