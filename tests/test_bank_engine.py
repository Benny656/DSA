"""
Unit tests for the BankEngine core logic, banking rules, and transaction consistency.
"""
from datetime import datetime, timedelta
import unittest

from core.bank_engine import BankEngine
from core.models import TransactionType, TransactionStatus


class TestBankEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BankEngine()
        self.engine.create_account("101", "Alice", 1000.0)
        self.engine.create_account("102", "Bob", 500.0)

    def test_account_creation_validation(self):
        # Existing account
        ok, msg = self.engine.create_account("101", "Duplicate Alice", 100.0)
        self.assertFalse(ok)

        # Invalid account number
        ok, msg = self.engine.create_account("abc", "Charlie", 100.0)
        self.assertFalse(ok)

        # Negative balance
        ok, msg = self.engine.create_account("103", "Charlie", -50.0)
        self.assertFalse(ok)

    def test_deposit_and_withdrawal(self):
        # Deposit
        ok, msg, tx = self.engine.execute_immediate(TransactionType.DEPOSIT, "101", None, 500.0)
        self.assertTrue(ok)
        self.assertEqual(self.engine.get_account("101").balance, 1500.0)

        # Successful Withdrawal
        ok, msg, tx = self.engine.execute_immediate(TransactionType.WITHDRAWAL, "101", None, 200.0)
        self.assertTrue(ok)
        self.assertEqual(self.engine.get_account("101").balance, 1300.0)

        # Insufficient Funds Withdrawal
        ok, msg, tx = self.engine.execute_immediate(TransactionType.WITHDRAWAL, "101", None, 5000.0)
        self.assertFalse(ok)
        self.assertEqual(self.engine.get_account("101").balance, 1300.0)
        self.assertEqual(tx.status, TransactionStatus.FAILED)

    def test_atomic_transfer(self):
        # Transfer 300 from 101 to 102
        ok, msg, tx = self.engine.execute_immediate(TransactionType.TRANSFER, "101", "102", 300.0)
        self.assertTrue(ok)
        self.assertEqual(self.engine.get_account("101").balance, 700.0)
        self.assertEqual(self.engine.get_account("102").balance, 800.0)

        # Transfer exceeding balance
        ok, msg, tx = self.engine.execute_immediate(TransactionType.TRANSFER, "101", "102", 2000.0)
        self.assertFalse(ok)
        # Balances remain unchanged
        self.assertEqual(self.engine.get_account("101").balance, 700.0)
        self.assertEqual(self.engine.get_account("102").balance, 800.0)

    def test_fifo_circular_queue_processing(self):
        self.engine.queue_regular_transaction(TransactionType.DEPOSIT, "101", None, 100.0)
        self.engine.queue_regular_transaction(TransactionType.DEPOSIT, "101", None, 200.0)

        # Process first queued
        ok, msg, tx1 = self.engine.process_next_regular()
        self.assertTrue(ok)
        self.assertEqual(tx1.amount, 100.0)
        self.assertEqual(self.engine.get_account("101").balance, 1100.0)

        # Process second queued
        ok, msg, tx2 = self.engine.process_next_regular()
        self.assertTrue(ok)
        self.assertEqual(tx2.amount, 200.0)
        self.assertEqual(self.engine.get_account("101").balance, 1300.0)

    def test_priority_min_heap_processing(self):
        now = datetime.now()
        due_later = now + timedelta(minutes=10)
        due_earlier = now + timedelta(minutes=2)

        self.engine.queue_priority_transaction(TransactionType.DEPOSIT, "101", None, 100.0, due_later)
        self.engine.queue_priority_transaction(TransactionType.DEPOSIT, "101", None, 200.0, due_earlier)

        # Earliest due time must be processed first
        ok, msg, tx = self.engine.process_next_priority()
        self.assertTrue(ok)
        self.assertEqual(tx.amount, 200.0)
        self.assertEqual(tx.priority_due_time, due_earlier)

    def test_transaction_undo_stack(self):
        # Perform deposit of 400 into 101 -> balance 1400
        self.engine.execute_immediate(TransactionType.DEPOSIT, "101", None, 400.0)
        self.assertEqual(self.engine.get_account("101").balance, 1400.0)

        # Undo deposit -> balance reverts to 1000
        ok, msg, tx = self.engine.undo_last_transaction()
        self.assertTrue(ok)
        self.assertEqual(self.engine.get_account("101").balance, 1000.0)

        # Perform transfer of 250 from 101 to 102
        self.engine.execute_immediate(TransactionType.TRANSFER, "101", "102", 250.0)
        self.assertEqual(self.engine.get_account("101").balance, 750.0)
        self.assertEqual(self.engine.get_account("102").balance, 750.0)

        # Undo transfer -> 101 has 1000, 102 has 500
        ok, msg, tx = self.engine.undo_last_transaction()
        self.assertTrue(ok)
        self.assertEqual(self.engine.get_account("101").balance, 1000.0)
        self.assertEqual(self.engine.get_account("102").balance, 500.0)

    def test_seed_demo_and_fraud_cycle_detection(self):
        self.engine.seed_demo_data()
        cycles = self.engine.detect_fraud_cycles_dfs()
        self.assertGreaterEqual(len(cycles), 1)
        # Verify 101, 102, 103 are in the circular transfer loop
        found = False
        for c in cycles:
            if "101" in c and "102" in c and "103" in c:
                found = True
                break
        self.assertTrue(found, "Cycle among 101, 102, 103 should be detected by DFS")


if __name__ == "__main__":
    unittest.main()
