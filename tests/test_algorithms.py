"""
Unit tests for Sorting and Searching algorithms.
"""
import unittest

from algorithms.sorting import merge_sort, quick_sort
from algorithms.searching import linear_search, binary_search, hash_search
from core.models import Account
from data_structures.hash_table import HashTable


class TestSortingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.sample_data = [450.0, 120.5, 990.0, 50.0, 310.2, 50.0, 1200.0]

    def test_merge_sort_ascending(self):
        sorted_arr, comp = merge_sort(self.sample_data)
        self.assertEqual(sorted_arr, sorted(self.sample_data))
        self.assertGreater(comp, 0)

    def test_merge_sort_descending(self):
        sorted_arr, comp = merge_sort(self.sample_data, reverse=True)
        self.assertEqual(sorted_arr, sorted(self.sample_data, reverse=True))

    def test_quick_sort_ascending(self):
        sorted_arr, comp = quick_sort(self.sample_data)
        self.assertEqual(sorted_arr, sorted(self.sample_data))
        self.assertGreater(comp, 0)

    def test_quick_sort_descending(self):
        sorted_arr, comp = quick_sort(self.sample_data, reverse=True)
        self.assertEqual(sorted_arr, sorted(self.sample_data, reverse=True))

    def test_already_sorted_and_reversed(self):
        sorted_in = [1, 2, 3, 4, 5, 6, 7]
        m_out, _ = merge_sort(sorted_in)
        q_out, _ = quick_sort(sorted_in)
        self.assertEqual(m_out, sorted_in)
        self.assertEqual(q_out, sorted_in)


class TestSearchingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.accounts = [
            Account("101", "Alice", 1000.0),
            Account("102", "Bob", 2000.0),
            Account("103", "Charlie", 3000.0),
            Account("104", "David", 4000.0),
            Account("105", "Emma", 5000.0)
        ]
        self.ht = HashTable()
        for a in self.accounts:
            self.ht.put(a.account_number, a)

    def test_linear_search(self):
        acc, comp, _ = linear_search(self.accounts, "103")
        self.assertIsNotNone(acc)
        self.assertEqual(acc.holder_name, "Charlie")
        self.assertEqual(comp, 3)

        not_found, comp_nf, _ = linear_search(self.accounts, "999")
        self.assertIsNone(not_found)
        self.assertEqual(comp_nf, 5)

    def test_binary_search(self):
        acc, comp, _ = binary_search(self.accounts, "104")
        self.assertIsNotNone(acc)
        self.assertEqual(acc.holder_name, "David")
        self.assertLessEqual(comp, 4)

        not_found, _, _ = binary_search(self.accounts, "999")
        self.assertIsNone(not_found)

    def test_hash_search(self):
        acc, comp, _ = hash_search(self.ht, "102")
        self.assertIsNotNone(acc)
        self.assertEqual(acc.holder_name, "Bob")
        self.assertGreaterEqual(comp, 1)

        not_found, _, _ = hash_search(self.ht, "999")
        self.assertIsNone(not_found)


if __name__ == "__main__":
    unittest.main()
