"""
Performance Analysis & Benchmarking Module.
Generates synthetic datasets of 1,000 to 100,000 transactions/accounts,
measures execution times with time.perf_counter(), and generates
comparative performance curves using Matplotlib.
"""
from datetime import datetime, timedelta
import random
import time
from typing import Callable, Dict, List, Tuple

import matplotlib
# Use Agg or TkAgg depending on environment
import matplotlib.pyplot as plt

from core.models import Account, Transaction, TransactionType, TransactionStatus
from data_structures.hash_table import HashTable
from algorithms.sorting import merge_sort, quick_sort
from algorithms.searching import linear_search, binary_search, hash_search


def generate_synthetic_accounts(n: int) -> Tuple[List[Account], HashTable]:
    """Generate n synthetic accounts and populate both a list and a HashTable."""
    accounts = []
    ht = HashTable(capacity=max(16, n * 2))

    for i in range(1, n + 1):
        acc_num = f"{100000 + i}"
        name = f"Customer_{i}"
        balance = round(random.uniform(500.0, 500000.0), 2)
        acc = Account(account_number=acc_num, holder_name=name, balance=balance)
        accounts.append(acc)
        ht.put(acc_num, acc)

    return accounts, ht


def generate_synthetic_transactions(n: int) -> List[Transaction]:
    """Generate n synthetic transaction records."""
    transactions = []
    base_time = datetime(2026, 1, 1)

    for i in range(1, n + 1):
        tx_type = random.choice([TransactionType.DEPOSIT, TransactionType.WITHDRAWAL, TransactionType.TRANSFER])
        src = str(random.randint(100001, 100500))
        dst = str(random.randint(100501, 101000)) if tx_type == TransactionType.TRANSFER else None
        amt = round(random.uniform(10.0, 50000.0), 2)
        ts = base_time + timedelta(seconds=i * random.randint(10, 300))

        tx = Transaction(
            tx_id=f"SYN{i}",
            tx_type=tx_type,
            from_account=src,
            to_account=dst,
            amount=amt,
            timestamp=ts,
            status=TransactionStatus.COMPLETED
        )
        transactions.append(tx)

    return transactions


def benchmark_searching(sizes: List[int] = None) -> Dict[str, List]:
    """
    Benchmark Linear Search, Binary Search, and Hash Table lookup
    across varying dataset sizes.
    Returns dictionary with sizes and elapsed times in milliseconds.
    """
    if sizes is None:
        sizes = [1000, 5000, 10000, 25000, 50000, 100000]

    results = {
        "sizes": [],
        "linear_ms": [],
        "binary_ms": [],
        "hash_ms": [],
        "linear_comparisons": [],
        "binary_comparisons": [],
        "hash_comparisons": []
    }

    for size in sizes:
        accounts, ht = generate_synthetic_accounts(size)
        # Search target at roughly 80% mark to test realistic search
        target_idx = int(size * 0.8)
        target_acc_num = accounts[target_idx].account_number

        # Sorted list for binary search
        sorted_accounts = sorted(accounts, key=lambda a: a.account_number)

        # 1. Linear Search
        t0 = time.perf_counter()
        acc1, comp1, _ = linear_search(accounts, target_acc_num)
        t_lin = (time.perf_counter() - t0) * 1000

        # 2. Binary Search (averaged over 50 runs due to microsecond scale)
        t0 = time.perf_counter()
        for _ in range(50):
            acc2, comp2, _ = binary_search(sorted_accounts, target_acc_num)
        t_bin = ((time.perf_counter() - t0) / 50) * 1000

        # 3. Hash Table Search (averaged over 50 runs)
        t0 = time.perf_counter()
        for _ in range(50):
            acc3, comp3, _ = hash_search(ht, target_acc_num)
        t_hash = ((time.perf_counter() - t0) / 50) * 1000

        results["sizes"].append(size)
        results["linear_ms"].append(round(t_lin, 4))
        results["binary_ms"].append(round(t_bin, 4))
        results["hash_ms"].append(round(t_hash, 4))
        results["linear_comparisons"].append(comp1)
        results["binary_comparisons"].append(comp2)
        results["hash_comparisons"].append(comp3)

    return results


def benchmark_sorting(sizes: List[int] = None) -> Dict[str, List]:
    """
    Benchmark Merge Sort vs Quick Sort across varying transaction dataset sizes.
    Returns execution times in milliseconds and comparison counts.
    """
    if sizes is None:
        sizes = [1000, 2500, 5000, 10000, 25000]

    results = {
        "sizes": [],
        "merge_ms": [],
        "quick_ms": [],
        "merge_comparisons": [],
        "quick_comparisons": []
    }

    for size in sizes:
        txs = generate_synthetic_transactions(size)

        # Merge Sort
        t0 = time.perf_counter()
        sorted_merge, comp_merge = merge_sort(txs, key=lambda tx: tx.amount)
        t_merge = (time.perf_counter() - t0) * 1000

        # Quick Sort
        t0 = time.perf_counter()
        sorted_quick, comp_quick = quick_sort(txs, key=lambda tx: tx.amount)
        t_quick = (time.perf_counter() - t0) * 1000

        results["sizes"].append(size)
        results["merge_ms"].append(round(t_merge, 3))
        results["quick_ms"].append(round(t_quick, 3))
        results["merge_comparisons"].append(comp_merge)
        results["quick_comparisons"].append(comp_quick)

    return results


def plot_search_benchmark(results: Dict[str, List], save_path: str = None) -> plt.Figure:
    """Create Matplotlib figure comparing Search algorithms."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=100)
    fig.patch.set_facecolor('#0f172a')

    for ax in (ax1, ax2):
        ax.set_facecolor('#1e293b')
        ax.grid(True, linestyle='--', alpha=0.3, color='#94a3b8')
        ax.tick_params(colors='#e2e8f0', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    sizes = results["sizes"]

    # Plot 1: Execution Time (ms)
    ax1.plot(sizes, results["linear_ms"], marker='o', color='#ef4444', linewidth=2, label='Linear O(N)')
    ax1.plot(sizes, results["binary_ms"], marker='s', color='#3b82f6', linewidth=2, label='Binary O(log N)')
    ax1.plot(sizes, results["hash_ms"], marker='^', color='#10b981', linewidth=2, label='Hash Table O(1)')
    ax1.set_title("Search Time vs Dataset Size", color='#f8fafc', fontsize=10, fontweight='bold')
    ax1.set_xlabel("Number of Accounts", color='#cbd5e1', fontsize=9)
    ax1.set_ylabel("Execution Time (ms)", color='#cbd5e1', fontsize=9)
    ax1.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)

    # Plot 2: Comparisons
    ax2.plot(sizes, results["linear_comparisons"], marker='o', color='#ef4444', linewidth=2, label='Linear')
    ax2.plot(sizes, results["binary_comparisons"], marker='s', color='#3b82f6', linewidth=2, label='Binary')
    ax2.plot(sizes, results["hash_comparisons"], marker='^', color='#10b981', linewidth=2, label='Hash Table')
    ax2.set_title("Key Comparisons vs Dataset Size", color='#f8fafc', fontsize=10, fontweight='bold')
    ax2.set_xlabel("Number of Accounts", color='#cbd5e1', fontsize=9)
    ax2.set_ylabel("Comparison Count", color='#cbd5e1', fontsize=9)
    ax2.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
    return fig


def plot_sort_benchmark(results: Dict[str, List], save_path: str = None) -> plt.Figure:
    """Create Matplotlib figure comparing Sorting algorithms."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=100)
    fig.patch.set_facecolor('#0f172a')

    for ax in (ax1, ax2):
        ax.set_facecolor('#1e293b')
        ax.grid(True, linestyle='--', alpha=0.3, color='#94a3b8')
        ax.tick_params(colors='#e2e8f0', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    sizes = results["sizes"]

    # Plot 1: Execution Time (ms)
    ax1.plot(sizes, results["merge_ms"], marker='o', color='#8b5cf6', linewidth=2, label='Merge Sort O(N log N)')
    ax1.plot(sizes, results["quick_ms"], marker='s', color='#06b6d4', linewidth=2, label='Quick Sort O(N log N)')
    ax1.set_title("Sorting Time vs Transaction Count", color='#f8fafc', fontsize=10, fontweight='bold')
    ax1.set_xlabel("Number of Transactions", color='#cbd5e1', fontsize=9)
    ax1.set_ylabel("Execution Time (ms)", color='#cbd5e1', fontsize=9)
    ax1.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)

    # Plot 2: Comparisons
    ax2.plot(sizes, results["merge_comparisons"], marker='o', color='#8b5cf6', linewidth=2, label='Merge Sort')
    ax2.plot(sizes, results["quick_comparisons"], marker='s', color='#06b6d4', linewidth=2, label='Quick Sort')
    ax2.set_title("Comparisons vs Transaction Count", color='#f8fafc', fontsize=10, fontweight='bold')
    ax2.set_xlabel("Number of Transactions", color='#cbd5e1', fontsize=9)
    ax2.set_ylabel("Comparison Count", color='#cbd5e1', fontsize=9)
    ax2.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc', fontsize=8)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
    return fig
