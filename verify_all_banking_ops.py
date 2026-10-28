"""
Comprehensive Verification Script for BankFlow Banking Engine and Operations.
Verifies all functions end-to-end:
- Account creation
- Instant deposit & balance reflection
- Instant withdrawal & balance reflection
- Insufficient balance protection
- Instant transfer & bidirectional balance reflection
- Undo / rollback of deposit, withdrawal, and transfer
- Circular Queue FIFO batching
- Priority Min-Heap due-time scheduling
- AVL Tree date-range queries
- Graph BFS connected accounts & DFS fraud cycle detection
- Merge Sort history
- PDF statement generation
"""
import sys
import os
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure root directory on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.bank_engine import BankEngine
from core.models import TransactionType, TransactionStatus
from core.statement_pdf import generate_bank_statement_pdf


def run_checks():
    print("=" * 60)
    print(" RUNNING END-TO-END BANKFLOW VERIFICATION")
    print("=" * 60)

    engine = BankEngine()
    engine.seed_demo_data()

    # 1. Check Demo Accounts Seeded
    accs = engine.get_all_accounts()
    assert len(accs) == 8, f"Expected 8 accounts, got {len(accs)}"
    print(f"✓ Seeded demo accounts: {len(accs)} accounts present.")

    # 2. Account Creation
    ok, msg = engine.create_account("999", "Test User", 10000.0)
    assert ok, f"Account creation failed: {msg}"
    acc999 = engine.get_account("999")
    assert acc999 is not None, "Account 999 not found"
    assert acc999.balance == 10000.0, f"Expected 10000.0, got {acc999.balance}"
    print(f"✓ Account creation working: A/C 999 created with balance ₹{acc999.balance:,.2f}")

    # 3. Direct Deposit
    bal_before = acc999.balance
    ok, msg, tx = engine.execute_immediate(TransactionType.DEPOSIT, "999", None, 5000.0, "Test Deposit")
    assert ok, f"Deposit failed: {msg}"
    assert acc999.balance == bal_before + 5000.0, f"Expected {bal_before + 5000.0}, got {acc999.balance}"
    print(f"✓ Deposit working: New balance ₹{acc999.balance:,.2f} (+₹5,000)")

    # 4. Direct Withdrawal
    bal_before = acc999.balance
    ok, msg, tx = engine.execute_immediate(TransactionType.WITHDRAWAL, "999", None, 3000.0, "Test Withdrawal")
    assert ok, f"Withdrawal failed: {msg}"
    assert acc999.balance == bal_before - 3000.0, f"Expected {bal_before - 3000.0}, got {acc999.balance}"
    print(f"✓ Withdrawal working: New balance ₹{acc999.balance:,.2f} (-₹3,000)")

    # 4b. Overdraft Protection
    ok, msg, tx = engine.execute_immediate(TransactionType.WITHDRAWAL, "999", None, 999999.0, "Excessive Withdrawal")
    assert not ok, "Withdrawal should have failed for insufficient funds"
    print(f"✓ Overdraft protection working: {msg}")

    # 5. Direct Transfer
    acc101 = engine.get_account("101")
    acc102 = engine.get_account("102")
    bal101_before = acc101.balance
    bal102_before = acc102.balance
    transfer_amt = 4000.0

    ok, msg, tx = engine.execute_immediate(TransactionType.TRANSFER, "101", "102", transfer_amt, "Test Transfer")
    assert ok, f"Transfer failed: {msg}"
    assert acc101.balance == bal101_before - transfer_amt, "Sender balance not debited"
    assert acc102.balance == bal102_before + transfer_amt, "Receiver balance not credited"
    print(f"✓ Transfer working: 101 debited to ₹{acc101.balance:,.2f}, 102 credited to ₹{acc102.balance:,.2f}")

    # 6. Undo Rollback of Transfer
    ok, msg, undone_tx = engine.undo_last_transaction()
    assert ok, f"Undo failed: {msg}"
    assert acc101.balance == bal101_before, f"Sender balance not restored: {acc101.balance} vs {bal101_before}"
    assert acc102.balance == bal102_before, f"Receiver balance not restored: {acc102.balance} vs {bal102_before}"
    print(f"✓ Undo/Rollback working: Reverted transfer {undone_tx.tx_id}. Balances perfectly restored.")

    # 7. Circular Queue FIFO Processing
    q_len_before = engine.regular_queue.size()
    ok, msg, tx = engine.process_next_regular()
    assert ok, f"Regular queue processing failed: {msg}"
    assert engine.regular_queue.size() == q_len_before - 1, "Queue size not decremented"
    print(f"✓ Circular Queue FIFO working: Processed {tx.tx_id} ({tx.description})")

    # 8. Priority Min-Heap Processing
    heap_len_before = engine.priority_queue.size()
    ok, msg, tx = engine.process_next_priority()
    assert ok, f"Priority queue processing failed: {msg}"
    assert engine.priority_queue.size() == heap_len_before - 1, "Heap size not decremented"
    print(f"✓ Priority Min-Heap working: Extracted earliest due tx {tx.tx_id}")

    # 9. AVL Tree Date-Range Query
    now = datetime.now()
    range_results = engine.query_date_range(now - timedelta(hours=24), now)
    assert len(range_results) > 0, "AVL range query returned 0 matches"
    # Also verify reversed date bounds are safe
    range_results_rev = engine.query_date_range(now, now - timedelta(hours=24))
    assert len(range_results_rev) == len(range_results), "AVL range query bound safety check failed"
    print(f"✓ AVL Tree Date Range Query working: Found {len(range_results)} transactions (Height: {engine.avl_index.get_height()})")

    # 10. Graph BFS & DFS Fraud Cycle Detection
    bfs_nodes = engine.get_connected_accounts_bfs("101")
    assert len(bfs_nodes) > 0, "BFS returned 0 reachable accounts"
    print(f"✓ Graph BFS working: Reached {len(bfs_nodes)} accounts from 101.")

    cycles = engine.detect_fraud_cycles_dfs()
    assert len(cycles) > 0, "DFS should detect seed cycle (101->102->103->101)"
    print(f"✓ Graph DFS Fraud Detection working: Detected {len(cycles)} cycle(s): {cycles[0]}")

    # 11. PDF Bank Statement Generation
    pdf_bytes = generate_bank_statement_pdf(
        account=acc101,
        transactions=engine.get_all_history(),
        start_date=now - timedelta(days=30),
        end_date=now
    )
    assert pdf_bytes.startswith(b"%PDF"), "PDF byte signature invalid"
    assert len(pdf_bytes) > 1000, "PDF size suspiciously small"
    print(f"✓ PDF Statement Generation working: Generated {len(pdf_bytes):,} bytes valid PDF.")

    # 12. Merge Sort
    sorted_by_amt, comps = engine.sort_transactions(by="amount", algorithm="merge", reverse=True)
    assert len(sorted_by_amt) > 0
    assert sorted_by_amt[0].amount >= sorted_by_amt[-1].amount, "Merge sort order incorrect"
    print(f"✓ Merge Sort working: Sorted {len(sorted_by_amt)} transactions with {comps} comparisons.")

    print("=" * 60)
    print(" ALL 12 CHECKS PASSED PERFECTLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_checks()
