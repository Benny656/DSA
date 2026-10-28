# Comprehensive System Report: BankFlow / NovaTrust

**BankFlow** (also presented as **NovaTrust**) is an enterprise-grade banking transaction processing platform engineered from **first principles** in Python 3. It serves a unique dual purpose:
1. **An authentic commercial retail & corporate banking platform**: Providing real-world financial workflows such as account onboarding, direct transfers, priority RTGS/wire scheduling, institutional PDF bank statement generation, and AML (Anti-Money Laundering) fraud detection.
2. **An interactive Data Structures & Algorithms (DSA) engine**: Implementing all fundamental data structures and algorithms from scratch (without relying on Python's built-in dictionaries, `heapq`, `deque`, or sorting shortcuts for core operations) to demonstrate empirical computer science principles under real banking workloads.

---

## 1. System Architecture & Dual-Facing Interfaces

The application offers two complementary interfaces backed by a unified processing engine:

```text
                      ┌───────────────────────────────────────────────┐
                      │            User Presentation Layer            │
                      ├───────────────────────┬───────────────────────┤
                      │  Modern Next.js Web   │ Desktop Tkinter GUI   │
                      │  (Port 3000 / React)  │ (Standalone Python)   │
                      └───────────┬───────────┴───────────┬───────────┘
                                  │ REST API              │ Direct Calls
                      ┌───────────▼───────────────────────▼───────────┐
                      │    FastAPI Server / Application Controller    │
                      │               (api_server.py)                 │
                      └───────────────────────┬───────────────────────┘
                                              │
                      ┌───────────────────────▼───────────────────────┐
                      │           BankEngine Core Controller          │
                      │             (core/bank_engine.py)             │
                      └───────────────────────┬───────────────────────┘
                                              │
         ┌────────────────────────────────────┴────────────────────────────────────┐
         │             Underlying First-Principles DSA Subsystems                  │
         ├───────────────────────┬───────────────────────┬─────────────────────────┤
         │ Hash Table (O(1))     │ Circular Queue (FIFO) │ Min-Heap (Priority)     │
         │ Doubly Linked List    │ LIFO Stack (Rollback) │ AVL Tree (Range Search) │
         │ Directed Graph (AML)  │ Sorting (Merge/Quick) │ Searching Benchmarks    │
         └───────────────────────┴───────────────────────┴─────────────────────────┘
```

1. **Next.js Web Portal (`http://localhost:3000`)**: A sleek dark-mode financial dashboard featuring real-time account balances, transfer modals, institutional PDF downloads, and a toggleable **"⚡ Live DSA Engine Inspector"** that exposes the internal memory representations of all data structures.
2. **Desktop GUI (`main.py` / `gui/app.py`)**: A native Python Tkinter application with tabbed controls, real-time logging, and embedded **Matplotlib** performance benchmark plots.
3. **FastAPI REST Backend (`api_server.py`)**: A RESTful API providing full CRUD operations, transaction processing endpoints, live DSA memory introspection, and ReportLab PDF streaming.

---

## 2. Core Functional Capabilities

### A. Account Management & Portfolio Overview
- **Account Onboarding**: Creates accounts with unique numerical identifiers, customer legal names, and initial balances.
- **Instant Account Lookup**: Fetches account records, total available balance, and live status.
- **Global Portfolio Aggregation**: Tracks total vault liquidity across all retail and commercial customer accounts.

### B. Multi-Tiered Transaction Processing Engine
The system categorizes banking transactions into three operational execution tiers:
1. **Instant Direct Settlement**:
   - **Cash Deposits & Over-the-counter Withdrawals**: Verifies balance sufficiency and atomically updates account balances.
   - **Peer-to-Peer (P2P) Direct Transfers**: Atomically debits the sender and credits the recipient while recording ledger nodes.
2. **Standard Clearing (Batch / FIFO Processing)**:
   - Queues transactions to simulate standard ACH or clearinghouse batches.
   - Supports single-step FIFO dequeuing as well as automated full-batch clearance.
3. **Priority Wire / RTGS Settlement (Time-Scheduled)**:
   - Handles institutional high-value wires and urgent RTGS transfers.
   - Prioritized by **earliest target settlement deadline** rather than order of arrival.
   - Supports earliest-deadline first (EDF) dequeuing.

### C. Safe Transaction Rollback & Dispute Resolution
- **Atomic Undo**: When a transaction dispute or processing failure occurs, the engine reverses the last completed transaction.
- Accurately restores both sender and receiver balances and flags the transaction status as `ROLLED_BACK`.

### D. Institutional Audit-Grade Bank Statements
- **Instant Mini-Statements**: Pulls the most recent $K$ transactions for any given account in reverse chronological order.
- **Official PDF Generation (`core/statement_pdf.py`)**:
  - Built with **ReportLab** to generate formal, bank-grade PDF account statements.
  - Formatted with institutional letterheads, IFSC/branch routing, account summary boxes (Opening Balance, Total Credits, Total Debits, Closing Balance), and detailed transaction tables with running balances.

### E. Financial Crime & AML (Anti-Money Laundering) Analysis
- **Counterparty Reachability (BFS)**: Explores multi-hop transaction paths originating from a target account to track fund flows.
- **Circular Layering Detection (DFS)**: Automatically scans all transfer relationships for directed cycles (e.g., `Account A ➔ Account B ➔ Account C ➔ Account A`), flagging classic money laundering layering patterns.

---

## 3. Data Structures Implemented from First Principles

Every core operation is tied directly to a custom, hand-crafted data structure:

| Functional Area | Data Structure | File Reference | Theoretical Complexity | Implementation Detail |
|---|---|---|---|---|
| **Account Storage** | **Hash Table** with Separate Chaining | `data_structures/hash_table.py` | **O(1)** average lookup / insert | Custom polynomial hash function, singly linked bucket chains, and dynamic table resizing ($2\times$) when load factor $\lambda > 0.75$. |
| **Standard Clearing** | **Circular FIFO Queue** | `data_structures/circular_queue.py` | **O(1)** enqueue / dequeue | Fixed-size array with modulo pointer arithmetic (`front = (front + 1) % capacity`) avoiding element shifting. |
| **Priority RTGS/Wires** | **Binary Min-Heap** | `data_structures/min_heap.py` | **O(log N)** push / pop | Array-based complete binary tree comparing timestamps. Implements recursive/iterative `bubble_up` and `bubble_down`. |
| **Audit Ledger** | **Doubly Linked List** | `data_structures/doubly_linked_list.py` | **O(1)** append, **O(K)** reverse retrieval | Forward (`next`) and backward (`prev`) node links. Enables generating mini-statements from the tail without traversing the entire ledger. |
| **Transaction Rollback** | **LIFO Stack** | `data_structures/stack.py` | **O(1)** push / pop | Strictly tracks successful transactions for atomic ledger reversal. |
| **Date-Range Filtering** | **Self-Balancing AVL Tree** | `data_structures/avl_tree.py` | **O(log N + K)** range search | Height-balanced binary search tree maintaining $\|h_L - h_R\| \le 1$ through LL, RR, LR, and RL rotations. Indexed by ISO transaction timestamps. |
| **AML Fraud Detection** | **Directed Transaction Graph** | `data_structures/graph.py` | **O(V + E)** traversal | Adjacency list storing directed transaction edges. Uses **BFS** with a visited set for reachability and **DFS** with a recursion stack for cycle detection. |

---

## 4. Algorithms & Empirical Benchmarking Suite

The system includes dedicated benchmark modules (`performance/benchmarks.py`):

### 1. Search Algorithm Comparison
- Compares **Linear Search ($O(N)$)**, **Binary Search ($O(\log N)$)**, and **Hash Table Lookup ($O(1)$)**.
- Tests across sample scales ($N = 1,000$ to $100,000$).
- Measures actual runtime using `time.perf_counter()`, demonstrating the asymptotic difference between linear scanning and constant-time hashing.

### 2. Sorting Algorithm Comparison
- Compares **Merge Sort** (divide-and-conquer, stable, guaranteed $O(N \log N)$) vs. **Quick Sort** (in-place partitioning, median-of-three pivot, average $O(N \log N)$).
- Tracks both **execution duration (ms)** and exact **element comparison counts**.

---

## 5. Summary of Workspace Structure

```text
bank_website/
├── APPLICATION_REPORT.md        # Comprehensive system specification report
├── api_server.py                # FastAPI backend exposing REST endpoints & PDF downloads
├── main.py                      # Desktop entry point (launches Tkinter GUI)
├── README.md                    # System documentation and usage guide
├── requirements.txt             # Dependencies (fastapi, uvicorn, reportlab, matplotlib)
├── algorithms/
│   ├── searching.py             # Linear, Binary, and Hash lookup implementations
│   └── sorting.py               # Merge Sort and Quick Sort implementations
├── core/
│   ├── bank_engine.py           # Master controller integrating DSA with banking logic
│   ├── models.py                # Account and Transaction entity definitions
│   └── statement_pdf.py         # Institutional PDF generation engine
├── data_structures/             # Custom DSA implementations from scratch
│   ├── avl_tree.py              # Self-balancing BST
│   ├── circular_queue.py        # Circular buffer FIFO queue
│   ├── doubly_linked_list.py    # Bidirectional audit chain
│   ├── graph.py                 # Graph with BFS hops and DFS cycle detection
│   ├── hash_table.py            # Chained hash table with dynamic rehash
│   ├── min_heap.py              # Priority queue based on binary min-heap
│   └── stack.py                 # LIFO undo ledger stack
├── frontend/                    # Next.js 14 web application
│   ├── src/app/page.tsx         # Full banking dashboard + DSA Engine Inspector
│   └── src/services/api.ts      # Axios/Fetch client connecting to FastAPI
├── gui/
│   └── app.py                   # Multi-tab Tkinter desktop application
├── performance/
│   └── benchmarks.py            # Automated time.perf_counter() benchmark harness
└── tests/
    └── test_dsa.py              # 25 automated unit tests covering all data structures
```

---

## 6. How to Run the Application

### Option A: Next.js Web Interface + FastAPI Backend
1. **Start the Backend API**:
   ```bash
   python api_server.py
   ```
   *Runs at `http://localhost:8000`*

2. **Start the Next.js Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   *Runs at `http://localhost:3000`*

### Option B: Python Tkinter Desktop Interface
```bash
python main.py
```

### Option C: Run Automated Test Suite
```bash
python -m unittest discover -s tests -v
```
