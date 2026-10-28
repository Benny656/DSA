"""
Doubly Linked List implementation for transaction history & mini-statements.
Allows bidirectional traversal and fast O(1) appends.
"""
from typing import Any, Callable, List, Optional


class DLLNode:
    """Node for Doubly Linked List."""
    def __init__(self, data: Any):
        self.data: Any = data
        self.prev: Optional['DLLNode'] = None
        self.next: Optional['DLLNode'] = None


class DoublyLinkedList:
    """
    Doubly Linked List maintaining head and tail pointers.
    Provides bidirectional traversal and mini-statement generation.
    """
    def __init__(self):
        self.head: Optional[DLLNode] = None
        self.tail: Optional[DLLNode] = None
        self.count: int = 0

    def is_empty(self) -> bool:
        """Check if list is empty."""
        return self.count == 0

    def size(self) -> int:
        """Return number of nodes in list."""
        return self.count

    def append(self, data: Any) -> None:
        """Append node to end of list (O(1))."""
        node = DLLNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.count += 1

    def prepend(self, data: Any) -> None:
        """Prepend node to front of list (O(1))."""
        node = DLLNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.count += 1

    def to_list_forward(self) -> List[Any]:
        """Traverse from head to tail (oldest to newest)."""
        result = []
        curr = self.head
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def to_list_backward(self) -> List[Any]:
        """Traverse from tail to head (newest to oldest)."""
        result = []
        curr = self.tail
        while curr is not None:
            result.append(curr.data)
            curr = curr.prev
        return result

    def get_last_n(self, n: int = 10, filter_fn: Optional[Callable[[Any], bool]] = None) -> List[Any]:
        """
        Retrieve up to n most recent transactions (traversing backward from tail).
        Optionally applies a filter_fn (e.g. match account_number).
        """
        result = []
        curr = self.tail
        while curr is not None and len(result) < n:
            if filter_fn is None or filter_fn(curr.data):
                result.append(curr.data)
            curr = curr.prev
        return result

    def remove_last(self) -> Optional[Any]:
        """Remove and return data from the tail of the list."""
        if self.tail is None:
            return None
        data = self.tail.data
        if self.head == self.tail:
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self.count -= 1
        return data

    def clear(self) -> None:
        """Empty the linked list."""
        self.head = None
        self.tail = None
        self.count = 0

    def __len__(self) -> int:
        return self.count

    def __iter__(self):
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next
