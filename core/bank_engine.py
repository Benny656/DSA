"""
BankEngine: The Central Business Logic Engine.
Integrates all manual data structures and algorithms into a cohesive,
transaction-safe banking processing system.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Tuple

from core.models import Account, Transaction, TransactionType, TransactionStatus
from data_structures.hash_table import HashTable
from data_structures.circular_queue import CircularQueue
from data_structures.min_heap import MinHeap
from data_structures.doubly_linked_list import DoublyLinkedList
from data_structures.stack import Stack
from data_structures.avl_tree import AVLTree
from data_structures.graph import TransactionGraph
from algorithms.sorting import merge_sort, quick_sort
from algorithms.searching import compare_all_searches


class BankEngine:
    """
    Main Banking Engine managing:
    - Accounts in Hash Table (separate chaining, resizing > 0.75)
    - Regular transactions in Circular Queue (FIFO)
    - Priority transactions in Min-Heap (earliest due time)
    - History & Mini-statements in Doubly Linked List
    - Transaction Rollback / Undo in LIFO Stack
    - Date-Range Queries in AVL Tree
    - Fund Transfers & Cycle Detection in Directed Graph
    """
    def __init__(self):
        # 1. Accounts storage
        self.accounts: HashTable = HashTable(capacity=16)

        # 2. Regular transaction FIFO queue
        self.regular_queue: CircularQueue = CircularQueue(capacity=64)

        # 3. Priority transaction Min-Heap
        self.priority_queue: MinHeap = MinHeap()

        # 4. Transaction history & mini-statements
        self.history: DoublyLinkedList = DoublyLinkedList()

        # 5. Undo Stack
        self.undo_stack: Stack = Stack()

        # 6. AVL Tree indexed by timestamp
        self.avl_index: AVLTree = AVLTree()

        # 7. Transfer graph for fraud & network analysis
        self.transfer_graph: TransactionGraph = TransactionGraph()

        # Transaction ID counter
        self._tx_counter: int = 1000

    def _next_tx_id(self) -> str:
        self._tx_counter += 1
        return f"TXN{self._tx_counter}"

    # -------------------------------------------------------------
    # Account Management (Hash Table)
    # -------------------------------------------------------------
    def create_account(self, account_number: str, holder_name: str, opening_balance: float = 0.0) -> Tuple[bool, str]:
        """Create a new account and store in Hash Table."""
        acc_num = str(account_number).strip()
        name = str(holder_name).strip()

        if not acc_num.isdigit() or len(acc_num) < 3:
            return False, "Account number must be digits only with at least 3 digits."
        if not name:
            return False, "Account holder name cannot be empty."
        if opening_balance < 0:
            return False, "Opening balance cannot be negative."

        if self.accounts.contains(acc_num):
            return False, f"Account {acc_num} already exists."

        account = Account(account_number=acc_num, holder_name=name, balance=opening_balance)
        self.accounts.put(acc_num, account)
        self.transfer_graph.add_vertex(acc_num)
        return True, f"Account {acc_num} successfully created for {name} with balance ₹{opening_balance:,.2f}"

    def get_account(self, account_number: str) -> Optional[Account]:
        """Fetch account from Hash Table."""
        return self.accounts.get(str(account_number).strip())

    def get_all_accounts(self) -> List[Account]:
        """Retrieve all accounts currently stored."""
        return self.accounts.get_all_values()

    def get_total_bank_balance(self) -> float:
        """Calculate sum of balances across all accounts."""
        return sum(acc.balance for acc in self.get_all_accounts())

    # -------------------------------------------------------------
    # Transaction Queueing
    # -------------------------------------------------------------
    def queue_regular_transaction(
        self,
        tx_type: TransactionType,
        from_account: str,
        to_account: Optional[str],
        amount: float,
        description: str = ""
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """Add regular transaction to Circular Queue (FIFO)."""
        tx, err = self._validate_and_build_tx(tx_type, from_account, to_account, amount, description)
        if not tx:
            return False, err, None

        self.regular_queue.enqueue(tx)
        return True, f"Transaction {tx.tx_id} queued in Circular Queue (FIFO).", tx

    def queue_priority_transaction(
        self,
        tx_type: TransactionType,
        from_account: str,
        to_account: Optional[str],
        amount: float,
        due_time: datetime,
        description: str = ""
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """Add priority transaction to Min-Heap scheduled by due_time."""
        tx, err = self._validate_and_build_tx(tx_type, from_account, to_account, amount, description, due_time=due_time)
        if not tx:
            return False, err, None

        # Min-heap key is the due_time datetime
        self.priority_queue.insert(due_time, tx)
        return True, f"Priority Transaction {tx.tx_id} scheduled in Min-Heap (Due: {due_time.strftime('%H:%M:%S')}).", tx

    def _validate_and_build_tx(
        self,
        tx_type: TransactionType,
        from_account: str,
        to_account: Optional[str],
        amount: float,
        description: str,
        due_time: Optional[datetime] = None
    ) -> Tuple[Optional[Transaction], str]:
        from_acc = str(from_account).strip()
        to_acc = str(to_account).strip() if to_account else None

        if amount <= 0:
            return None, "Transaction amount must be greater than zero."

        if not self.accounts.contains(from_acc):
            return None, f"Source account {from_acc} does not exist."

        if tx_type == TransactionType.TRANSFER:
            if not to_acc:
                return None, "Transfer requires a destination account."
            if from_acc == to_acc:
                return None, "Cannot transfer funds to the same account."
            if not self.accounts.contains(to_acc):
                return None, f"Destination account {to_acc} does not exist."

        tx = Transaction(
            tx_id=self._next_tx_id(),
            tx_type=tx_type,
            from_account=from_acc,
            to_account=to_acc,
            amount=amount,
            timestamp=datetime.now(),
            priority_due_time=due_time,
            description=description
        )
        return tx, ""

    # -------------------------------------------------------------
    # Transaction Processing Engine
    # -------------------------------------------------------------
    def process_next_regular(self) -> Tuple[bool, str, Optional[Transaction]]:
        """Process the front transaction from Circular Queue."""
        if self.regular_queue.is_empty():
            return False, "Circular Queue is empty.", None

        tx = self.regular_queue.dequeue()
        success, msg = self._execute_transaction(tx)
        return success, msg, tx

    def process_next_priority(self) -> Tuple[bool, str, Optional[Transaction]]:
        """Process the earliest scheduled transaction from Min-Heap."""
        if self.priority_queue.is_empty():
            return False, "Priority Min-Heap is empty.", None

        tx = self.priority_queue.extract_min()
        success, msg = self._execute_transaction(tx)
        return success, msg, tx

    def process_all_queued(self) -> Tuple[int, int, List[str]]:
        """Process all queued priority and regular transactions."""
        processed_count = 0
        failed_count = 0
        logs = []

        # Process priority queue first (earliest due time)
        while not self.priority_queue.is_empty():
            success, msg, tx = self.process_next_priority()
            if success:
                processed_count += 1
            else:
                failed_count += 1
            logs.append(f"[Priority] {msg}")

        # Then process circular queue FIFO
        while not self.regular_queue.is_empty():
            success, msg, tx = self.process_next_regular()
            if success:
                processed_count += 1
            else:
                failed_count += 1
            logs.append(f"[Regular] {msg}")

        return processed_count, failed_count, logs

    def execute_immediate(
        self,
        tx_type: TransactionType,
        from_account: str,
        to_account: Optional[str],
        amount: float,
        description: str = ""
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """Execute a transaction immediately without queueing."""
        tx, err = self._validate_and_build_tx(tx_type, from_account, to_account, amount, description)
        if not tx:
            return False, err, None

        success, msg = self._execute_transaction(tx)
        return success, msg, tx

    def _execute_transaction(self, tx: Transaction) -> Tuple[bool, str]:
        """
        Executes a transaction with strict atomic balance consistency,
        records in history (DLL), indexes in AVL Tree, updates graph,
        and pushes onto Undo Stack if successful.
        """
        source = self.accounts.get(tx.from_account)
        if not source:
            tx.status = TransactionStatus.FAILED
            tx.failure_reason = f"Account {tx.from_account} does not exist"
            self._record_transaction(tx)
            return False, f"Failed: {tx.failure_reason}"

        if tx.tx_type == TransactionType.DEPOSIT:
            source.balance = round(source.balance + tx.amount, 2)
            tx.status = TransactionStatus.COMPLETED
            self._record_transaction(tx)
            self.undo_stack.push(tx)
            return True, f"Deposited ₹{tx.amount:,.2f} into account {source.account_number}. New Balance: ₹{source.balance:,.2f}"

        elif tx.tx_type == TransactionType.WITHDRAWAL:
            if source.balance < tx.amount:
                tx.status = TransactionStatus.FAILED
                tx.failure_reason = f"Insufficient funds (Balance: ₹{source.balance:,.2f}, Required: ₹{tx.amount:,.2f})"
                self._record_transaction(tx)
                return False, f"Failed: {tx.failure_reason}"

            source.balance = round(source.balance - tx.amount, 2)
            tx.status = TransactionStatus.COMPLETED
            self._record_transaction(tx)
            self.undo_stack.push(tx)
            return True, f"Withdrew ₹{tx.amount:,.2f} from account {source.account_number}. New Balance: ₹{source.balance:,.2f}"

        elif tx.tx_type == TransactionType.TRANSFER:
            dest = self.accounts.get(tx.to_account)
            if not dest:
                tx.status = TransactionStatus.FAILED
                tx.failure_reason = f"Destination account {tx.to_account} does not exist"
                self._record_transaction(tx)
                return False, f"Failed: {tx.failure_reason}"

            if source.balance < tx.amount:
                tx.status = TransactionStatus.FAILED
                tx.failure_reason = f"Insufficient funds in sender {source.account_number} (Balance: ₹{source.balance:,.2f})"
                self._record_transaction(tx)
                return False, f"Failed: {tx.failure_reason}"

            # Atomic debit and credit
            source.balance = round(source.balance - tx.amount, 2)
            dest.balance = round(dest.balance + tx.amount, 2)

            tx.status = TransactionStatus.COMPLETED
            self._record_transaction(tx)
            self.undo_stack.push(tx)

            # Record edge in transfer graph
            self.transfer_graph.add_transfer(
                from_acc=source.account_number,
                to_acc=dest.account_number,
                amount=tx.amount,
                tx_id=tx.tx_id,
                timestamp=tx.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )

            return True, f"Transferred ₹{tx.amount:,.2f} from {source.account_number} to {dest.account_number} successfully."

        return False, "Unknown transaction type"

    def _record_transaction(self, tx: Transaction) -> None:
        """Record transaction in Doubly Linked List and AVL Tree."""
        self.history.append(tx)
        self.avl_index.insert(tx.timestamp, tx)

    # -------------------------------------------------------------
    # Undo / Rollback Engine (Stack)
    # -------------------------------------------------------------
    def undo_last_transaction(self) -> Tuple[bool, str, Optional[Transaction]]:
        """
        Safely roll back the most recently completed transaction from the Stack.
        Ensures balance safety and updates transfer graph.
        """
        if self.undo_stack.is_empty():
            return False, "Undo Stack is empty. No completed transactions to revert.", None

        tx: Transaction = self.undo_stack.pop()

        source = self.accounts.get(tx.from_account)
        dest = self.accounts.get(tx.to_account) if tx.to_account else None

        if tx.tx_type == TransactionType.DEPOSIT:
            # Reversing a deposit requires debiting source
            if source.balance < tx.amount:
                # Put back on stack since rollback cannot be safely completed
                self.undo_stack.push(tx)
                return False, f"Cannot undo deposit: Account {source.account_number} has insufficient funds to deduct ₹{tx.amount:,.2f}.", tx

            source.balance = round(source.balance - tx.amount, 2)
            tx.status = TransactionStatus.UNDONE

            undo_record = Transaction(
                tx_id=self._next_tx_id(),
                tx_type=TransactionType.WITHDRAWAL,
                from_account=source.account_number,
                to_account=None,
                amount=tx.amount,
                timestamp=datetime.now(),
                status=TransactionStatus.COMPLETED,
                description=f"ROLLBACK/UNDO of Deposit {tx.tx_id}"
            )
            self._record_transaction(undo_record)
            return True, f"Successfully reversed Deposit {tx.tx_id}. Deducted ₹{tx.amount:,.2f} from {source.account_number}.", tx

        elif tx.tx_type == TransactionType.WITHDRAWAL:
            # Reversing a withdrawal requires crediting source
            source.balance = round(source.balance + tx.amount, 2)
            tx.status = TransactionStatus.UNDONE

            undo_record = Transaction(
                tx_id=self._next_tx_id(),
                tx_type=TransactionType.DEPOSIT,
                from_account=source.account_number,
                to_account=None,
                amount=tx.amount,
                timestamp=datetime.now(),
                status=TransactionStatus.COMPLETED,
                description=f"ROLLBACK/UNDO of Withdrawal {tx.tx_id}"
            )
            self._record_transaction(undo_record)
            return True, f"Successfully reversed Withdrawal {tx.tx_id}. Credited ₹{tx.amount:,.2f} back to {source.account_number}.", tx

        elif tx.tx_type == TransactionType.TRANSFER:
            # Reversing a transfer requires debiting recipient and crediting sender
            if dest and dest.balance < tx.amount:
                self.undo_stack.push(tx)
                return False, f"Cannot undo transfer: Destination account {dest.account_number} has insufficient funds (₹{dest.balance:,.2f}) to refund ₹{tx.amount:,.2f}.", tx

            if dest:
                dest.balance = round(dest.balance - tx.amount, 2)
            if source:
                source.balance = round(source.balance + tx.amount, 2)

            tx.status = TransactionStatus.UNDONE
            self.transfer_graph.remove_transfer(tx.tx_id)

            undo_record = Transaction(
                tx_id=self._next_tx_id(),
                tx_type=TransactionType.TRANSFER,
                from_account=dest.account_number if dest else "-",
                to_account=source.account_number if source else "-",
                amount=tx.amount,
                timestamp=datetime.now(),
                status=TransactionStatus.COMPLETED,
                description=f"ROLLBACK/UNDO of Transfer {tx.tx_id}"
            )
            self._record_transaction(undo_record)
            return True, f"Successfully reversed Transfer {tx.tx_id}. Re-credited ₹{tx.amount:,.2f} to {source.account_number} from {dest.account_number}.", tx

        return False, "Unrecognized transaction undo type.", tx

    # -------------------------------------------------------------
    # Mini-Statements and History (Doubly Linked List)
    # -------------------------------------------------------------
    def get_mini_statement(self, account_number: str, limit: int = 5) -> List[Transaction]:
        """
        Generate mini-statement using Doubly Linked List backward traversal.
        Retrieves the last `limit` transactions involving this account.
        """
        acc_num = str(account_number).strip()
        filter_fn = lambda tx: tx.from_account == acc_num or tx.to_account == acc_num
        return self.history.get_last_n(n=limit, filter_fn=filter_fn)

    def get_all_history(self, newest_first: bool = True) -> List[Transaction]:
        """Get full history using DLL traversal."""
        if newest_first:
            return self.history.to_list_backward()
        return self.history.to_list_forward()

    # -------------------------------------------------------------
    # Date Range Querying (AVL Tree)
    # -------------------------------------------------------------
    def query_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Retrieve transactions within a date range using AVL Tree range query."""
        return self.avl_index.range_query(start_date, end_date)

    # -------------------------------------------------------------
    # Sorting Demonstration (Merge Sort & Quick Sort)
    # -------------------------------------------------------------
    def sort_transactions(
        self,
        by: str = "amount",
        algorithm: str = "merge",
        reverse: bool = False
    ) -> Tuple[List[Transaction], int]:
        """
        Sort transaction history by amount or date using manual Merge Sort or Quick Sort.
        Returns (sorted_transactions, comparison_count).
        """
        txs = self.history.to_list_forward()
        if not txs:
            return [], 0

        if by == "amount":
            key_fn = lambda tx: tx.amount
        elif by == "date":
            key_fn = lambda tx: tx.timestamp
        else:
            key_fn = lambda tx: tx.tx_id

        if algorithm.lower() == "merge":
            return merge_sort(txs, key=key_fn, reverse=reverse)
        else:
            return quick_sort(txs, key=key_fn, reverse=reverse)

    # -------------------------------------------------------------
    # Account Lookup Comparison (Searching)
    # -------------------------------------------------------------
    def compare_account_lookup(self, account_number: str) -> Dict:
        """Compare Linear Search, Binary Search, and Hash Table lookup."""
        accounts = self.get_all_accounts()
        return compare_all_searches(accounts, self.accounts, account_number)

    # -------------------------------------------------------------
    # Graph Analysis: BFS & DFS
    # -------------------------------------------------------------
    def get_connected_accounts_bfs(self, start_account: str) -> List[Dict]:
        """Explore connected accounts using Breadth-First Search."""
        return self.transfer_graph.bfs_connected_accounts(str(start_account).strip())

    def detect_fraud_cycles_dfs(self) -> List[List[str]]:
        """Detect circular transfer patterns using Depth-First Search."""
        return self.transfer_graph.detect_circular_transfers()

    # -------------------------------------------------------------
    # Synthetic Data Seeding for College Demo
    # -------------------------------------------------------------
    def seed_demo_data(self) -> None:
        """
        Populates realistic demo accounts and transactions, including:
        - Regular accounts with various balances
        - Processed deposits, withdrawals, transfers
        - A circular transfer loop: 101 -> 102 -> 103 -> 101 for graph cycle demonstration
        - Queued transactions in Circular Queue and Min-Heap
        """
        # Clear existing data
        self.accounts = HashTable(capacity=16)
        self.regular_queue = CircularQueue(capacity=64)
        self.priority_queue = MinHeap()
        self.history = DoublyLinkedList()
        self.undo_stack = Stack()
        self.avl_index = AVLTree()
        self.transfer_graph = TransactionGraph()
        self._tx_counter = 1000

        # Create demo accounts
        sample_accounts = [
            ("101", "Aarav Sharma", 150000.0),
            ("102", "Priya Patel", 85000.0),
            ("103", "Rohan Mehta", 62000.0),
            ("104", "Sneha Rao", 120000.0),
            ("105", "Vikram Singh", 95000.0),
            ("106", "Ananya Iyer", 43000.0),
            ("107", "Karan Malhotra", 180000.0),
            ("108", "Neha Gupta", 74000.0),
        ]

        for acc_num, name, bal in sample_accounts:
            self.create_account(acc_num, name, bal)

        # Baseline timestamp
        now = datetime.now()

        # Execute some historical transactions with time offsets
        historical_ops = [
            (TransactionType.DEPOSIT, "101", None, 25000.0, now - timedelta(hours=5), "Salary Credit"),
            (TransactionType.WITHDRAWAL, "102", None, 5000.0, now - timedelta(hours=4), "ATM Cash Withdrawal"),
            (TransactionType.TRANSFER, "101", "102", 15000.0, now - timedelta(hours=3, minutes=30), "Consulting Fee"),
            (TransactionType.TRANSFER, "102", "103", 12000.0, now - timedelta(hours=3), "Equipment Purchase"),
            (TransactionType.TRANSFER, "103", "101", 10000.0, now - timedelta(hours=2, minutes=30), "Loan Repayment (Forms Cycle!)"),
            (TransactionType.TRANSFER, "104", "105", 22000.0, now - timedelta(hours=2), "Vendor Settlement"),
            (TransactionType.TRANSFER, "105", "106", 18000.0, now - timedelta(hours=1, minutes=30), "Contractor Payment"),
            (TransactionType.TRANSFER, "107", "108", 35000.0, now - timedelta(hours=1), "Intercompany Transfer"),
            (TransactionType.DEPOSIT, "106", None, 30000.0, now - timedelta(minutes=45), "Client Invoice Settlement"),
        ]

        for tx_type, src, dst, amt, ts, desc in historical_ops:
            tx = Transaction(
                tx_id=self._next_tx_id(),
                tx_type=tx_type,
                from_account=src,
                to_account=dst,
                amount=amt,
                timestamp=ts,
                description=desc
            )
            # Execute with specific timestamp
            source_acc = self.accounts.get(src)
            dest_acc = self.accounts.get(dst) if dst else None

            if tx_type == TransactionType.DEPOSIT:
                source_acc.balance = round(source_acc.balance + amt, 2)
            elif tx_type == TransactionType.WITHDRAWAL:
                source_acc.balance = round(source_acc.balance - amt, 2)
            elif tx_type == TransactionType.TRANSFER and dest_acc:
                source_acc.balance = round(source_acc.balance - amt, 2)
                dest_acc.balance = round(dest_acc.balance + amt, 2)
                self.transfer_graph.add_transfer(src, dst, amt, tx.tx_id, ts.strftime("%Y-%m-%d %H:%M:%S"))

            tx.status = TransactionStatus.COMPLETED
            self._record_transaction(tx)
            self.undo_stack.push(tx)

        # Queue pending regular transactions in Circular Queue
        self.queue_regular_transaction(TransactionType.TRANSFER, "106", "104", 5000.0, "Monthly Rent")
        self.queue_regular_transaction(TransactionType.DEPOSIT, "105", None, 14000.0, "Dividend Credit")
        self.queue_regular_transaction(TransactionType.WITHDRAWAL, "108", None, 4000.0, "Utility Payment")

        # Queue pending priority transactions in Min-Heap
        due1 = now + timedelta(minutes=15)
        due2 = now + timedelta(minutes=5)   # Earlier due time, should be processed first!
        due3 = now + timedelta(minutes=30)

        self.queue_priority_transaction(TransactionType.TRANSFER, "107", "101", 50000.0, due1, "Priority RTGS Settlement")
        self.queue_priority_transaction(TransactionType.WITHDRAWAL, "103", None, 8000.0, due2, "Urgent Hospital Payment")
        self.queue_priority_transaction(TransactionType.DEPOSIT, "102", None, 20000.0, due3, "Scheduled Cheque Deposit")
