"""
Circular Queue implementation for FIFO regular transaction processing.
Maintains front and rear pointers with modular arithmetic.
"""
from typing import Any, List, Optional


class CircularQueue:
    """
    Circular FIFO Queue implemented with a fixed-size circular array
    that dynamically resizes when full to prevent dropping transactions.
    """
    DEFAULT_CAPACITY = 64

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity: int = max(4, capacity)
        self.queue: List[Optional[Any]] = [None] * self.capacity
        self.front: int = 0
        self.rear: int = 0
        self.count: int = 0

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self.count == 0

    def is_full(self) -> bool:
        """Check if queue is full."""
        return self.count == self.capacity

    def size(self) -> int:
        """Return number of elements in queue."""
        return self.count

    def enqueue(self, item: Any) -> None:
        """Add item to rear of circular queue. Resizes if full."""
        if self.is_full():
            self._resize(self.capacity * 2)

        self.queue[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1

    def dequeue(self) -> Optional[Any]:
        """Remove and return front item from circular queue."""
        if self.is_empty():
            return None

        item = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item

    def peek(self) -> Optional[Any]:
        """View front item without removing."""
        if self.is_empty():
            return None
        return self.queue[self.front]

    def _resize(self, new_capacity: int) -> None:
        """Resize circular buffer to new capacity and realign front/rear."""
        new_queue = [None] * new_capacity
        for i in range(self.count):
            new_queue[i] = self.queue[(self.front + i) % self.capacity]
        self.queue = new_queue
        self.front = 0
        self.rear = self.count
        self.capacity = new_capacity

    def to_list(self) -> List[Any]:
        """Return list of elements in FIFO order."""
        items = []
        for i in range(self.count):
            items.append(self.queue[(self.front + i) % self.capacity])
        return items

    def clear(self) -> None:
        """Empty the queue."""
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def __len__(self) -> int:
        return self.count

    def __iter__(self):
        for item in self.to_list():
            yield item
