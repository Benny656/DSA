# NovaTrust / BankFlow: Efficient Bank Transaction Processing System Using Data Structures and Algorithms

A full-stack, enterprise-grade banking platform and algorithms demonstration system built from first principles in Python 3 with a modern **Next.js** frontend and an optional **Tkinter** desktop GUI.

---

## 🌟 Key Highlights

1. **Authentic Banking Experience (Customer & Commercial Facing)**:
   - Built in **Next.js** with clean, modern financial technology aesthetics.
   - Genuine banking terminology (Send Money, Priority Wire / RTGS, Instant Settlement, Cash Withdrawal, Over-the-counter Deposits, Dispute & Reversal).
   - No distracting algorithm jargon on consumer buttons.
2. **Institutional PDF Bank Statements**:
   - Generates authentic, audit-grade bank statements in PDF format using **ReportLab**.
   - Formatted with official bank letterhead, IFSC/Branch routing, account summary box (Opening Balance, Total Credits, Total Debits, Closing Balance), and a structured transaction table (Posting Date, Narration, Ref No, Dr/Cr amounts, Closing Balance, Status).
3. **⚡ Live DSA Engine Inspector & Control Lab (Behind-the-Scenes)**:
   - Dedicated toggleable console right inside the Next.js app (`⚡ DSA Engine Inspector`).
   - Gives professors, evaluators, and students total visibility and interactive control over:
     - **Hash Table**: Separate chaining bucket cards, chain lengths, collision counts, live load factor ($\lambda$ vs 0.75 threshold), and dynamic resize counter.
     - **Circular Queue (FIFO)**: Visual circular buffer showing active slots, `FRONT` pointer, and `REAR` pointer with step-by-step dequeue and batch drain controls.
     - **Binary Min-Heap**: Priority transaction tree with scheduled due times and bubble-up priority extraction.
     - **Doubly Linked List**: Bidirectional node chain showing head, tail, and tail-to-head backward traversal for instant mini-statements.
     - **LIFO Stack**: Rollback stack with top-of-stack inspection and safe atomic ledger reversal.
     - **AVL Tree**: Self-balancing BST indexed by datetime ($|h_L - h_R| \le 1$), supporting $O(\log N + K)$ chronological date-range queries.
     - **Graph (BFS & DFS)**: Adjacency list edge matrix, BFS multi-hop counterparty network tracer, and DFS cycle detection identifying circular money-laundering loops.
     - **Empirical Benchmarks**: Live measurement using `time.perf_counter()` comparing Searching ($O(N)$ vs $O(\log N)$ vs $O(1)$) and Sorting (Merge Sort vs Quick Sort).

---

## 🏛️ Architecture & Data Structures Implemented from First Principles

| # | Feature / Operation | Underlying Data Structure / Algorithm | File Location | Complexity |
|---|---|---|---|---|
| **1** | **Account Storage** | **Hash Table (Separate Chaining)** | `data_structures/hash_table.py` | **O(1)** avg lookup, resizes at $\lambda > 0.75$ |
| **2** | **Regular Clearing** | **Circular FIFO Queue** | `data_structures/circular_queue.py` | **O(1)** enqueue, **O(1)** dequeue with modular pointers |
| **3** | **Priority RTGS/Wires**| **Binary Min-Heap** | `data_structures/min_heap.py` | **O(log N)** scheduling by earliest due time |
| **4** | **Audit History** | **Doubly Linked List** | `data_structures/doubly_linked_list.py` | **O(1)** append, **O(K)** reverse mini-statement |
| **5** | **Transaction Rollback**| **LIFO Stack** | `data_structures/stack.py` | **O(1)** push/pop safe ledger undo |
| **6** | **Date-Range Reports** | **Self-Balancing AVL Tree** | `data_structures/avl_tree.py` | **O(log N)** insert, **O(log N + K)** range query |
| **7** | **Record Sorting** | **Merge Sort & Quick Sort** | `algorithms/sorting.py` | **O(N log N)** amount & date sorting |
| **8** | **Lookup Benchmarks** | **Linear, Binary & Hash Search** | `algorithms/searching.py` | Linear: **O(N)**, Binary: **O(log N)**, Hash: **O(1)** |
| **9** | **Anti-Fraud Security** | **Directed Graph (BFS & DFS)** | `data_structures/graph.py` | BFS: **O(V + E)** hops, DFS: **O(V + E)** cycle detection |
| **10**| **Statement Generator**| **Institutional PDF Engine** | `core/statement_pdf.py` | Professional ReportLab PDF statement builder |

---

## 🚀 How to Launch the Full Next.js System

### Prerequisites
- **Python 3.8+**
- **Node.js 18+** & npm

### Step 1: Install Backend & Frontend Dependencies
In the root directory:
```bash
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

### Step 2: Start the Python DSA Backend (FastAPI)
In Terminal 1:
```bash
python api_server.py
```
> Running at **`http://localhost:8000`**

### Step 3: Start the Next.js Frontend
In Terminal 2:
```bash
cd frontend
npm run dev
```
> Running at **`http://localhost:3000`**

Open **`http://localhost:3000`** in your browser.

---

## 🖥️ Alternative: Launch Desktop Tkinter GUI

If you want to demonstrate the standalone Python Tkinter desktop GUI:

```bash
python main.py
```

---

## 🧪 How to Run Automated Unit Tests

Run all 25 test cases verifying the manual data structures and algorithms from first principles:

```bash
python -m unittest discover -s tests -v
```

All 25 tests pass in milliseconds.

---

## 🎓 Evaluator Demonstration Walkthrough (Next.js)

1. **Consumer Bank Experience**:
   - Open `http://localhost:3000`.
   - Point out the clean commercial banking layout: Total Portfolio Wealth, Platinum card widget, active accounts list, and recent transaction activity.
   - Click **"Send Money"** or go to **Transfers & Clearing**:
     - Demonstrate a **Standard Transfer** (queues in Circular Queue).
     - Demonstrate a **Priority Wire / RTGS** (scheduled with due time in Min-Heap).
     - Demonstrate an **Instant Settlement** (immediate ledger update).
   - Go to **Official Statements**:
     - Filter transactions by account and period.
     - Click **"Download Official PDF Statement"**: opens an authentic PDF statement complete with official bank letterhead, customer summary, opening balance, debit/credit columns, and closing balance!
   - Go to **Anti-Fraud & Network**:
     - Click **"Run Circular Transfer Scan"**: flags the circular layering pattern `101 ➔ 102 ➔ 103 ➔ 101` characteristic of suspicious fund layering!

2. **Under-the-Hood DSA Inspection**:
   - Click the glowing **`⚡ DSA Engine Inspector`** button in the top navigation.
   - Show the evaluator the exact inner workings:
     - **Hash Table**: Inspect separate chaining bucket cards, live chain lengths, and load factor $\lambda \le 0.75$.
     - **Circular Queue**: Observe the circular array slots, `FRONT` and `REAR` pointers, and click **"Step: Process FIFO"** to watch the front item dequeued and processed in real time.
     - **Binary Min-Heap**: Show priority transactions ordered by due time and click **"Step: Process Min-Heap"** to extract the earliest due item.
     - **Doubly Linked List**: View bidirectional node pointers and backward mini-statement generation.
     - **LIFO Stack**: Show the top transaction waiting on the stack, click **"Execute Stack Rollback"**, and observe the ledger balance reversal.
     - **AVL Tree**: Observe tree height balancing and run an interactive chronological date-range query.
     - **Performance Benchmarks**: Run the live benchmark suite measuring execution times via `time.perf_counter()`.
