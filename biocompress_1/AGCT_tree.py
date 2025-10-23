from dataclasses import dataclass, field
from typing import Optional
from config import HEIGHT, CONTENT


@dataclass
class Node:
    level: int
    isLeaf: bool = False
    aBranch: Optional["Node"] = None
    cBranch: Optional["Node"] = None
    tBranch: Optional["Node"] = None
    gBranch: Optional["Node"] = None
    positions: list[int] = field(default_factory=list)


    def _child_for_base(self, base: str) -> Optional["Node"]:
        mapping = {
            "A": self.aBranch,
            "C": self.cBranch,
            "T": self.tBranch,
            "G": self.gBranch,
        }
        return mapping.get(base)

    def createPositions(self, string: str, position: int, i: int = 0):
        if not string or i >= len(string):
            return

        child = self._child_for_base(string[i])

        if child is None:
            return

        # Append once if leaf or first time we visit this child
        if child.isLeaf or not child.positions:
            child.positions.append(position)

        self._recurse_child(child, string, position, i + 1)

    def _recurse_child(self, child: "Node", s: str, position: int, i: int):
        if i < len(s):
            child.createPositions(s, position, i)



    def __str__(self) -> str:
        return self._format()

    def _format(self, indent: int = 0) -> str:
        pad = "  " * indent
        bits = [f"Node(level={self.level}"]
        if self.isLeaf: bits.append("isLeaf=True")
        if self.positions: bits.append(f"positions={self.positions}")
        head = pad + (", ".join(bits) + ")")

        lines = [head]
        for label, child in (
            ("A", self.aBranch),
            ("C", self.cBranch),
            ("T", self.tBranch),
            ("G", self.gBranch),
        ):
            if child is not None:
                lines.append(pad + f"  {label} →")
                lines.append(child._format(indent + 2))
        return "\n".join(lines)


def createChildren(node: Node, height: int):
    if node.level >= height:
        node.isLeaf = True
        return
    
    node.isLeaf=False

    node.aBranch = Node(level=node.level + 1)
    node.cBranch = Node(level=node.level + 1)
    node.tBranch = Node(level=node.level + 1)
    node.gBranch = Node(level=node.level + 1)

    createChildren(node.aBranch, height)
    createChildren(node.cBranch, height)
    createChildren(node.tBranch, height)
    createChildren(node.gBranch, height)


def createTree(height: int) -> Node:
    root = Node(level=0)
    createChildren(root, height)
    return root


def findFactor(string: str, tree: Node):
    curr = tree
    last_pos: Optional[list[int]] = None
    last_level: Optional[int] = None

    steps = min(HEIGHT, len(string))
    for i in range(steps):
        mapping = {
            "A": curr.aBranch,
            "C": curr.cBranch,
            "T": curr.tBranch,
            "G": curr.gBranch,
        }

        next_curr = mapping.get(string[i])
        if next_curr is None:
            return (None, None) 

        curr = next_curr

        if curr.positions:
            last_pos = curr.positions
            last_level = curr.level
        else:
            if (last_pos is not None and last_level is not None):
                return (last_pos, last_level)
            return (None, None) 

    if (last_pos is not None and last_level is not None):
        return (last_pos, last_level)
    return (None, None)


def main():
    # root = createTree(HEIGHT)
    # print(root)
    print("wrong file")

if __name__ == "__main__":
    main()
