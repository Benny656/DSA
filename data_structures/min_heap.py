"""
Binary Min-Heap implementation for Priority Transaction Scheduling.
Prioritizes transactions with earlier due times or higher priority weights.
"""
from typing import Any, List, Optional, Tuple


class MinHeapNode:
    """Entry stored in the Min-Heap."""
    def __init__(self, key: Any, value: Any):
        self.key: Any = key      # e.g., timestamp, due_time, or priority level
        self.value: Any = value  # Transaction object

    def __lt__(self, other: 'MinHeapNode') -> bool:
        return self.key < other.key


class MinHeap:
    """
    Binary Min-Heap implemented using a 0-indexed list from first principles.
    Parent(i) = (i - 1) // 2
    LeftChild(i) = 2*i + 1
    RightChild(i) = 2*i + 2
    """
    def __init__(self):
        self.heap: List[MinHeapNode] = []

    def is_empty(self) -> bool:
        """Check if heap has no elements."""
        return len(self.heap) == 0

    def size(self) -> int:
        """Return count of elements."""
        return len(self.heap)

    def insert(self, key: Any, value: Any) -> None:
        """Insert element and bubble up (shift up) to maintain min-heap property."""
        node = MinHeapNode(key, value)
        self.heap.append(node)
        self._shift_up(len(self.heap) - 1)

    def peek(self) -> Optional[Any]:
        """Return the highest priority (minimum key) item without removing."""
        if self.is_empty():
            return None
        return self.heap[0].value

    def peek_entry(self) -> Optional[Tuple[Any, Any]]:
        """Return (key, value) of minimum element without removing."""
        if self.is_empty():
            return None
        return self.heap[0].key, self.heap[0].value

    def extract_min(self) -> Optional[Any]:
        """Extract and return the item with the minimum key."""
        if self.is_empty():
            return None

        min_val = self.heap[0].value
        last_node = self.heap.pop()

        if not self.is_empty():
            self.heap[0] = last_node
            self._shift_down(0)

        return min_val

    def _shift_up(self, index: int) -> None:
        """Move element up to restore min-heap invariant."""
        curr = index
        while curr > 0:
            parent = (curr - 1) // 2
            if self.heap[curr] < self.heap[parent]:
                self.heap[curr], self.heap[parent] = self.heap[parent], self.heap[curr]
                curr = parent
            else:
                break

    def _shift_down(self, index: int) -> None:
        """Move element down to restore min-heap invariant."""
        curr = index
        size = len(self.heap)

        while True:
            left = 2 * curr + 1
            right = 2 * curr + 2
            smallest = curr

            if left < size and self.heap[left] < self.heap[smallest]:
                smallest = left

            if right < size and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest != curr:
                self.heap[curr], self.heap[smallest] = self.heap[smallest], self.heap[curr]
                curr = smallest
            else:
                break

    def to_list(self) -> List[Any]:
        """Return a copy of items in heap-storage order."""
        return [node.value for node in self.heap]

    def to_sorted_list(self) -> List[Any]:
        """Return items sorted by priority key without modifying original heap."""
        temp_heap = MinHeap()
        for node in self.heap:
            temp_heap.insert(node.key, node.value)

        sorted_items = []
        while not temp_heap.is_empty():
            sorted_items.append(temp_heap.extract_min())
        return sorted_items

    def clear(self) -> None:
        """Clear all entries."""
        self.heap = []

    def __len__(self) -> int:
        return len(self.heap)
