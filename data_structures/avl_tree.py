"""
AVL Tree implementation for Indexing Transactions by Date/Timestamp.
Self-balancing Binary Search Tree supporting efficient O(log N) insertions
and range queries for date-range financial reporting.
"""
from datetime import datetime
from typing import Any, List, Optional, Tuple


class AVLNode:
    """Node in the AVL Tree."""
    def __init__(self, key: Any, value: Any):
        self.key: Any = key          # datetime or timestamp
        self.values: List[Any] = [value]  # Handles duplicate timestamps cleanly
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height: int = 1


class AVLTree:
    """
    Self-balancing AVL Tree indexed by date/timestamp.
    Maintains strict balance property |height(L) - height(R)| <= 1 via rotations.
    """
    def __init__(self):
        self.root: Optional[AVLNode] = None
        self.total_nodes: int = 0
        self.total_entries: int = 0

    def _height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _balance_factor(self, node: Optional[AVLNode]) -> int:
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """Right rotation around node y."""
        x = y.left
        t2 = x.right

        # Perform rotation
        x.right = y
        y.left = t2

        # Update heights
        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """Left rotation around node x."""
        y = x.right
        t2 = y.left

        # Perform rotation
        y.left = x
        x.right = t2

        # Update heights
        self._update_height(x)
        self._update_height(y)

        return y

    def insert(self, key: Any, value: Any) -> None:
        """Insert a key-value pair into the AVL tree."""
        self.root = self._insert_node(self.root, key, value)
        self.total_entries += 1

    def _insert_node(self, node: Optional[AVLNode], key: Any, value: Any) -> AVLNode:
        if node is None:
            self.total_nodes += 1
            return AVLNode(key, value)

        if key == node.key:
            # Same timestamp, append to existing node values
            node.values.append(value)
            return node
        elif key < node.key:
            node.left = self._insert_node(node.left, key, value)
        else:
            node.right = self._insert_node(node.right, key, value)

        # Update height of current node
        self._update_height(node)

        # Rebalance
        balance = self._balance_factor(node)

        # Case 1: Left-Left
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)

        # Case 2: Right-Right
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)

        # Case 3: Left-Right
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key: Any) -> List[Any]:
        """Find and return all values associated with key."""
        curr = self.root
        while curr is not None:
            if key == curr.key:
                return list(curr.values)
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return []

    def range_query(self, start_key: Any, end_key: Any) -> List[Any]:
        """
        Return all transactions whose key falls in [start_key, end_key],
        ordered chronologically.
        """
        results = []
        self._range_query_helper(self.root, start_key, end_key, results)
        return results

    def _range_query_helper(self, node: Optional[AVLNode], start_key: Any, end_key: Any, results: List[Any]) -> None:
        if node is None:
            return

        # If start_key < node.key, left subtree might have qualifying nodes
        if start_key < node.key:
            self._range_query_helper(node.left, start_key, end_key, results)

        # If node.key is within [start_key, end_key], add its values
        if start_key <= node.key <= end_key:
            results.extend(node.values)

        # If end_key > node.key, right subtree might have qualifying nodes
        if end_key > node.key:
            self._range_query_helper(node.right, start_key, end_key, results)

    def inorder(self) -> List[Any]:
        """Return all values in ascending order of keys."""
        results = []
        self._inorder_helper(self.root, results)
        return results

    def _inorder_helper(self, node: Optional[AVLNode], results: List[Any]) -> None:
        if node is not None:
            self._inorder_helper(node.left, results)
            results.extend(node.values)
            self._inorder_helper(node.right, results)

    def get_height(self) -> int:
        """Return the height of the tree."""
        return self._height(self.root)

    def size(self) -> int:
        """Return total entries indexed."""
        return self.total_entries

    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self.root is None

    def clear(self) -> None:
        """Clear the tree."""
        self.root = None
        self.total_nodes = 0
        self.total_entries = 0
