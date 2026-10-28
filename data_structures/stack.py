"""
Stack implementation for Transaction Undo operations (LIFO).
Supports safe reversal of the most recent completed transactions.
"""
from typing import Any, List, Optional


class StackNode:
    """Node for manual Stack implementation."""
    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional['StackNode'] = None


class Stack:
    """
    LIFO Stack implemented with linked nodes from first principles.
    Used to track completed transactions for safe rollback/undo operations.
    """
    def __init__(self):
        self.top: Optional[StackNode] = None
        self.count: int = 0

    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return self.top is None

    def size(self) -> int:
        """Return number of elements on stack."""
        return self.count

    def push(self, data: Any) -> None:
        """Push item onto stack (O(1))."""
        node = StackNode(data)
        node.next = self.top
        self.top = node
        self.count += 1

    def pop(self) -> Optional[Any]:
        """Pop and return top item from stack (O(1))."""
        if self.is_empty():
            return None
        data = self.top.data
        self.top = self.top.next
        self.count -= 1
        return data

    def peek(self) -> Optional[Any]:
        """View top item without removing (O(1))."""
        if self.is_empty():
            return None
        return self.top.data

    def to_list(self) -> List[Any]:
        """Return elements from top to bottom."""
        result = []
        curr = self.top
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def clear(self) -> None:
        """Empty the stack."""
        self.top = None
        self.count = 0

    def __len__(self) -> int:
        return self.count

    def __iter__(self):
        curr = self.top
        while curr is not None:
            yield curr.data
            curr = curr.next
