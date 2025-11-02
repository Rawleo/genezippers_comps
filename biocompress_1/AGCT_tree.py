from dataclasses import dataclass, field
from typing import Optional
from config import HEIGHT


@dataclass(slots=True)
class Node:
    level: int
    is_leaf: bool = False
    a_branch: Optional["Node"] = None
    c_branch: Optional["Node"] = None
    t_branch: Optional["Node"] = None
    g_branch: Optional["Node"] = None
    positions: list[int] = field(default_factory=list)


    def _child_for_base(self, base: str) -> Optional["Node"]:
        mapping = {
            "A": self.a_branch,
            "C": self.c_branch,
            "T": self.t_branch,
            "G": self.g_branch,
        }
        return mapping.get(base)

    def create_positions(self, string: str, position: int, i: int = 0):
        if not string or i >= len(string):
            return

        child = self._child_for_base(string[i])

        if child is None:
            return

        # Append once if leaf or first time we visit this child
        if child.is_leaf or not child.positions:
            child.positions.append(position)

        self._recurse_child(child, string, position, i + 1)

    def _recurse_child(self, child: "Node", s: str, position: int, i: int):
        if i < len(s):
            child.create_positions(s, position, i)


def create_children(node: Node, height: int):
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


def create_tree(height: int) -> Node:
    root = Node(level=0)
    create_children(root, height)
    return root


def find_factor(string: str, tree: Node):
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

