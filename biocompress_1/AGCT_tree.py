from dataclasses import dataclass, field
from typing import Optional
from config import HEIGHT


@dataclass
class Node:
    level: int
    is_leaf: bool = False
    a_branch: Optional["Node"] = None
    c_branch: Optional["Node"] = None
    t_branch: Optional["Node"] = None
    g_branch: Optional["Node"] = None
    positions: list[int] = field(default_factory=list)


    def _child_for_base(self, base):
        mapping = {
            "A": self.a_branch,
            "C": self.c_branch,
            "T": self.t_branch,
            "G": self.g_branch,
        }
        return mapping.get(base)
    

    def create_positions(self, string, position, i = 0):
        """
        Recursively adds the given position to the appropriate child node for each base in the string.
        
        Args:
            string (str): The DNA sequence to traverse.
            position (int): The position to record in the leaf node.
            i (int, optional): The current index in the string being processed. Defaults to 0.
        """
        if not string or i >= len(string):
            return

        child = self._child_for_base(string[i])

        if child is None:
            return

        # Append once if leaf or first time we visit this child
        if child.is_leaf or not child.positions:
            child.positions.append(position)

        self._recurse_child(child, string, position, i + 1)
        

    def _recurse_child(self, child, string, position, i):
        if i < len(string):
            child.create_positions(string, position, i)


def create_children(node, height):
    """
    Recursively builds a tree of Nodes up to the specified height, 
    setting leaf nodes and creating branches for each DNA base.
    
    Args:
        node (Node): The current node to expand.
        height (int): The maximum depth of the tree.
    """
    if node.level >= height:
        node.is_leaf = True
        return
    
    node.is_leaf=False

    node.a_branch = Node(level=node.level + 1)
    node.c_branch = Node(level=node.level + 1)
    node.t_branch = Node(level=node.level + 1)
    node.g_branch = Node(level=node.level + 1)

    create_children(node.a_branch, height)
    create_children(node.c_branch, height)
    create_children(node.t_branch, height)
    create_children(node.g_branch, height)



def create_tree(height):
    """
    Creates an AGCT tree of the specified height.

    Args:
        height (int): The height of the tree to create.

    Returns:
        Node: The root node of the constructed tree.
    """
    root = Node(level=0)
    create_children(root, height)
    return root


def find_factor(string, tree):
    curr = tree
    last_pos: Optional[list[int]] = None
    last_level: Optional[int] = None

    steps = min(HEIGHT, len(string))
    for i in range(steps):
        mapping = {
            "A": curr.a_branch,
            "C": curr.c_branch,
            "T": curr.t_branch,
            "G": curr.g_branch,
        }

        next_curr = mapping.get(string[i])
        if next_curr is None:
            return (None, None) 

        curr = next_curr

        if curr.positions:
            last_pos = curr.positions
            last_level = curr.level
        else:
            if last_pos is not None and last_level is not None:
                return (last_pos, last_level)
            return (None, None) 

    if last_pos is not None and last_level is not None:
        return (last_pos, last_level)
    return (None, None)

