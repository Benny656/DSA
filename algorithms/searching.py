"""
Searching algorithms implemented from first principles:
- Linear Search: O(N) sequential scan
- Binary Search: O(log N) divide-and-conquer on sorted list
- Hash Lookup: O(1) average constant time hash table query
Compares execution time and number of key comparisons.
"""
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from core.models import Account
from data_structures.hash_table import HashTable


def linear_search(
    accounts: List[Account],
    target_acc_num: str
) -> Tuple[Optional[Account], int, float]:
    """
    Linear Search: O(N) time complexity.
    Returns: (found_account, comparisons_count, elapsed_time_seconds)
    """
    start_time = time.perf_counter()
    comparisons = 0
    target_str = str(target_acc_num).strip()

    for acc in accounts:
        comparisons += 1
        if acc.account_number == target_str:
            elapsed = time.perf_counter() - start_time
            return acc, comparisons, elapsed

    elapsed = time.perf_counter() - start_time
    return None, comparisons, elapsed


def binary_search(
    sorted_accounts: List[Account],
    target_acc_num: str
) -> Tuple[Optional[Account], int, float]:
    """
    Binary Search: O(log N) time complexity.
    Assumes accounts are pre-sorted by account_number.
    Returns: (found_account, comparisons_count, elapsed_time_seconds)
    """
    start_time = time.perf_counter()
    comparisons = 0
    target_str = str(target_acc_num).strip()

    low = 0
    high = len(sorted_accounts) - 1

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        mid_acc = sorted_accounts[mid]

        if mid_acc.account_number == target_str:
            elapsed = time.perf_counter() - start_time
            return mid_acc, comparisons, elapsed
        elif mid_acc.account_number < target_str:
            low = mid + 1
        else:
            high = mid - 1

    elapsed = time.perf_counter() - start_time
    return None, comparisons, elapsed


def hash_search(
    hash_table: HashTable,
    target_acc_num: str
) -> Tuple[Optional[Account], int, float]:
    """
    Hash Table Search: O(1) average time complexity.
    Inspects hash index and counts chain traversal steps.
    Returns: (found_account, comparisons_count, elapsed_time_seconds)
    """
    start_time = time.perf_counter()
    target_str = str(target_acc_num).strip()

    index = hash_table._hash(target_str)
    curr = hash_table.buckets[index]
    comparisons = 0
    found = None

    while curr is not None:
        comparisons += 1
        if curr.key == target_str:
            found = curr.value
            break
        curr = curr.next

    elapsed = time.perf_counter() - start_time
    return found, comparisons, elapsed


def compare_all_searches(
    accounts: List[Account],
    hash_table: HashTable,
    target_acc_num: str
) -> Dict[str, Dict[str, Any]]:
    """
    Runs all three search algorithms on the same target and returns comparison stats.
    """
    # Pre-sort for binary search using merge sort or python sort for list prep
    sorted_accounts = sorted(accounts, key=lambda a: a.account_number)

    lin_acc, lin_comp, lin_time = linear_search(accounts, target_acc_num)
    bin_acc, bin_comp, bin_time = binary_search(sorted_accounts, target_acc_num)
    hash_acc, hash_comp, hash_time = hash_search(hash_table, target_acc_num)

    return {
        "linear": {
            "name": "Linear Search",
            "found": lin_acc is not None,
            "comparisons": lin_comp,
            "time_ms": lin_time * 1000,
            "time_sec": lin_time,
            "complexity": "O(N)"
        },
        "binary": {
            "name": "Binary Search",
            "found": bin_acc is not None,
            "comparisons": bin_comp,
            "time_ms": bin_time * 1000,
            "time_sec": bin_time,
            "complexity": "O(log N)"
        },
        "hash": {
            "name": "Hash Table Search",
            "found": hash_acc is not None,
            "comparisons": hash_comp,
            "time_ms": hash_time * 1000,
            "time_sec": hash_time,
            "complexity": "O(1) avg"
        }
    }
