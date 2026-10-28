"""
Unit tests for custom data structures implemented from first principles.
"""
from datetime import datetime, timedelta
import unittest

from data_structures.hash_table import HashTable
from data_structures.circular_queue import CircularQueue
from data_structures.min_heap import MinHeap
from data_structures.doubly_linked_list import DoublyLinkedList
from data_structures.stack import Stack
from data_structures.avl_tree import AVLTree
from data_structures.graph import TransactionGraph


class TestHashTable(unittest.TestCase):
    def test_basic_put_get_remove(self):
        ht = HashTable(capacity=8)
        ht.put("101", "Alice")
        ht.put("102", "Bob")
        ht.put("103", "Charlie")

        self.assertEqual(ht.get("101"), "Alice")
        self.assertEqual(ht.get("102"), "Bob")
        self.assertEqual(ht.get("103"), "Charlie")
        self.assertIsNone(ht.get("999"))
        self.assertTrue(ht.contains("101"))
        self.assertFalse(ht.contains("999"))

        # Update existing key
        ht.put("101", "Alice Smith")
        self.assertEqual(ht.get("101"), "Alice Smith")
        self.assertEqual(len(ht), 3)

        # Removal
        self.assertTrue(ht.remove("102"))
        self.assertFalse(ht.contains("102"))
        self.assertIsNone(ht.get("102"))
        self.assertEqual(len(ht), 2)

    def test_dynamic_resizing_at_load_factor(self):
        ht = HashTable(capacity=4)
        initial_capacity = ht.capacity

        # Insert items to exceed 0.75 load factor
        # 4 * 0.75 = 3 items max before resize
        ht.put("k1", "v1")
        ht.put("k2", "v2")
        ht.put("k3", "v3")
        self.assertLessEqual(ht.load_factor(), 0.75)

        ht.put("k4", "v4")  # 4 / 4 = 1.0 > 0.75 -> triggers resize to 8
        self.assertGreater(ht.capacity, initial_capacity)
        self.assertLessEqual(ht.load_factor(), 0.75)

        # Ensure all keys remain accessible
        for k in ["k1", "k2", "k3", "k4"]:
            self.assertTrue(ht.contains(k))


class TestCircularQueue(unittest.TestCase):
    def test_fifo_ordering(self):
        cq = CircularQueue(capacity=4)
        cq.enqueue("A")
        cq.enqueue("B")
        cq.enqueue("C")

        self.assertEqual(cq.size(), 3)
        self.assertEqual(cq.peek(), "A")

        self.assertEqual(cq.dequeue(), "A")
        self.assertEqual(cq.dequeue(), "B")

        cq.enqueue("D")
        cq.enqueue("E")

        # Drain remaining
        self.assertEqual(cq.dequeue(), "C")
        self.assertEqual(cq.dequeue(), "D")
        self.assertEqual(cq.dequeue(), "E")
        self.assertTrue(cq.is_empty())
        self.assertIsNone(cq.dequeue())

    def test_auto_resizing_on_overflow(self):
        cq = CircularQueue(capacity=4)
        for i in range(10):
            cq.enqueue(f"item_{i}")
        self.assertEqual(cq.size(), 10)
        self.assertEqual(cq.dequeue(), "item_0")


class TestMinHeap(unittest.TestCase):
    def test_min_extraction_order(self):
        heap = MinHeap()
        t1 = datetime(2026, 1, 1, 10, 0, 0)
        t2 = datetime(2026, 1, 1, 9, 30, 0)   # earliest
        t3 = datetime(2026, 1, 1, 11, 0, 0)
        t4 = datetime(2026, 1, 1, 9, 45, 0)

        heap.insert(t1, "Task1")
        heap.insert(t2, "Task2")
        heap.insert(t3, "Task3")
        heap.insert(t4, "Task4")

        self.assertEqual(heap.size(), 4)
        self.assertEqual(heap.peek(), "Task2")

        extracted = []
        while not heap.is_empty():
            extracted.append(heap.extract_min())

        self.assertEqual(extracted, ["Task2", "Task4", "Task1", "Task3"])


class TestDoublyLinkedList(unittest.TestCase):
    def test_bidirectional_traversal_and_mini_statement(self):
        dll = DoublyLinkedList()
        dll.append({"id": 1, "acc": "101"})
        dll.append({"id": 2, "acc": "102"})
        dll.append({"id": 3, "acc": "101"})
        dll.append({"id": 4, "acc": "103"})
        dll.append({"id": 5, "acc": "101"})

        self.assertEqual(dll.size(), 5)

        # Forward
        forward_ids = [item["id"] for item in dll.to_list_forward()]
        self.assertEqual(forward_ids, [1, 2, 3, 4, 5])

        # Backward (newest first)
        backward_ids = [item["id"] for item in dll.to_list_backward()]
        self.assertEqual(backward_ids, [5, 4, 3, 2, 1])

        # Mini statement for 101 (last 2 transactions)
        mini = dll.get_last_n(n=2, filter_fn=lambda x: x["acc"] == "101")
        self.assertEqual(len(mini), 2)
        self.assertEqual([m["id"] for m in mini], [5, 3])


class TestStack(unittest.TestCase):
    def test_lifo_undo(self):
        stack = Stack()
        stack.push("Tx1")
        stack.push("Tx2")
        stack.push("Tx3")

        self.assertEqual(stack.size(), 3)
        self.assertEqual(stack.peek(), "Tx3")

        self.assertEqual(stack.pop(), "Tx3")
        self.assertEqual(stack.pop(), "Tx2")
        self.assertEqual(stack.pop(), "Tx1")
        self.assertTrue(stack.is_empty())
        self.assertIsNone(stack.pop())


class TestAVLTree(unittest.TestCase):
    def test_avl_balancing_and_range_query(self):
        tree = AVLTree()
        now = datetime(2026, 1, 1, 12, 0, 0)

        # Insert strictly increasing timestamps (would degenerate linked list in BST)
        for i in range(15):
            t = now + timedelta(hours=i)
            tree.insert(t, f"tx_{i}")

        # In an AVL tree with 15 nodes, max height is ~4
        self.assertLessEqual(tree.get_height(), 5)
        self.assertEqual(tree.size(), 15)

        # Range query between hour 3 and hour 7
        t_start = now + timedelta(hours=3)
        t_end = now + timedelta(hours=7)
        results = tree.range_query(t_start, t_end)

        expected = [f"tx_{i}" for i in range(3, 8)]
        self.assertEqual(results, expected)


class TestTransactionGraph(unittest.TestCase):
    def test_bfs_connected_accounts(self):
        graph = TransactionGraph()
        # A -> B -> C
        graph.add_transfer("A", "B", 100.0, "T1", "2026-01-01")
        graph.add_transfer("B", "C", 50.0, "T2", "2026-01-01")

        connected = graph.bfs_connected_accounts("A")
        self.assertEqual(len(connected), 2)
        self.assertEqual(connected[0]["account"], "B")
        self.assertEqual(connected[0]["hops"], 1)
        self.assertEqual(connected[1]["account"], "C")
        self.assertEqual(connected[1]["hops"], 2)

    def test_dfs_cycle_detection(self):
        graph = TransactionGraph()
        # Create circular transfer cycle: A -> B -> C -> A
        graph.add_transfer("A", "B", 100.0, "T1", "2026-01-01")
        graph.add_transfer("B", "C", 100.0, "T2", "2026-01-01")
        graph.add_transfer("C", "A", 100.0, "T3", "2026-01-01")

        # Independent transfer D -> E
        graph.add_transfer("D", "E", 40.0, "T4", "2026-01-01")

        cycles = graph.detect_circular_transfers()
        self.assertEqual(len(cycles), 1)
        cycle = cycles[0]
        # Must start and end with same node, containing A, B, C
        self.assertEqual(cycle[0], cycle[-1])
        self.assertTrue(set(cycle).issuperset({"A", "B", "C"}))


if __name__ == "__main__":
    unittest.main()
