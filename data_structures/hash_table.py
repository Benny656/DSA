"""
Custom Hash Table implementation using Separate Chaining.
Dynamically resizes when load factor exceeds 0.75.
"""
from typing import Any, List, Optional, Tuple


class HashNode:
    """Node for separate chaining in Hash Table."""
    def __init__(self, key: str, value: Any):
        self.key: str = key
        self.value: Any = value
        self.next: Optional['HashNode'] = None


class HashTable:
    """
    Hash Table with Separate Chaining for collision resolution.
    Resizes automatically when load factor (items / capacity) > 0.75.
    """
    INITIAL_CAPACITY = 16
    MAX_LOAD_FACTOR = 0.75

    def __init__(self, capacity: int = INITIAL_CAPACITY):
        self.capacity: int = max(4, capacity)
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity
        self.count: int = 0
        self.resize_count: int = 0

    def _hash(self, key: str) -> int:
        """
        Polynomial rolling hash function.
        h = sum(ord(c) * 31^i) mod capacity
        """
        hash_val = 0
        prime = 31
        for i, char in enumerate(str(key)):
            hash_val = (hash_val * prime + ord(char)) % self.capacity
        return hash_val

    def load_factor(self) -> float:
        """Calculate current load factor."""
        return self.count / self.capacity if self.capacity > 0 else 0.0

    def put(self, key: str, value: Any) -> None:
        """Insert or update a key-value pair."""
        index = self._hash(key)
        head = self.buckets[index]
        curr = head

        # Check if key already exists
        while curr is not None:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next

        # Insert new node at head of chain (O(1))
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.count += 1

        # Check load factor and resize if needed
        if self.load_factor() > self.MAX_LOAD_FACTOR:
            self._resize(self.capacity * 2)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key. Returns None if not found."""
        index = self._hash(key)
        curr = self.buckets[index]
        while curr is not None:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return None

    def contains(self, key: str) -> bool:
        """Check if key exists in hash table."""
        return self.get(key) is not None

    def remove(self, key: str) -> bool:
        """Remove a key and return True if found and removed, False otherwise."""
        index = self._hash(key)
        curr = self.buckets[index]
        prev = None

        while curr is not None:
            if curr.key == key:
                if prev is None:
                    self.buckets[index] = curr.next
                else:
                    prev.next = curr.next
                self.count -= 1
                return True
            prev = curr
            curr = curr.next

        return False

    def _resize(self, new_capacity: int) -> None:
        """Resize table and rehash all elements."""
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [None] * self.capacity
        self.count = 0
        self.resize_count += 1

        for head in old_buckets:
            curr = head
            while curr is not None:
                self.put(curr.key, curr.value)
                curr = curr.next

    def get_all_keys(self) -> List[str]:
        """Return all keys."""
        keys = []
        for head in self.buckets:
            curr = head
            while curr is not None:
                keys.append(curr.key)
                curr = curr.next
        return keys

    def get_all_values(self) -> List[Any]:
        """Return all values."""
        values = []
        for head in self.buckets:
            curr = head
            while curr is not None:
                values.append(curr.value)
                curr = curr.next
        return values

    def get_all_entries(self) -> List[Tuple[str, Any]]:
        """Return list of (key, value) tuples."""
        entries = []
        for head in self.buckets:
            curr = head
            while curr is not None:
                entries.append((curr.key, curr.value))
                curr = curr.next
        return entries

    def bucket_collision_stats(self) -> dict:
        """Return statistics on collision distribution across buckets."""
        lengths = []
        for head in self.buckets:
            length = 0
            curr = head
            while curr is not None:
                length += 1
                curr = curr.next
            lengths.append(length)

        non_empty = [l for l in lengths if l > 0]
        collisions = [l for l in lengths if l > 1]
        max_chain = max(lengths) if lengths else 0
        avg_chain = sum(non_empty) / len(non_empty) if non_empty else 0.0

        return {
            "capacity": self.capacity,
            "total_items": self.count,
            "load_factor": round(self.load_factor(), 4),
            "non_empty_buckets": len(non_empty),
            "colliding_buckets": len(collisions),
            "max_chain_length": max_chain,
            "avg_chain_length": round(avg_chain, 2),
            "resize_count": self.resize_count
        }

    def __len__(self) -> int:
        return self.count

    def __iter__(self):
        for key in self.get_all_keys():
            yield key
