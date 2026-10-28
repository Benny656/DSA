"""
Tkinter Desktop GUI for the Bank Transaction Processing System.
Features:
- Dashboard with real-time statistics
- Account Management & Separate-Chaining Hash Table Inspector
- Transaction Queueing & Processing (Circular Queue & Min-Heap)
- Transaction History & Mini-Statements (Doubly Linked List & Undo Stack)
- Date-Range Queries (AVL Tree)
- Sorting Algorithms Comparison (Merge Sort vs Quick Sort)
- Searching Algorithms Comparison (Linear vs Binary vs Hash Table)
- Fraud Detection & Network Exploration (Graph BFS & DFS)
- Performance Analysis with embedded Matplotlib charts
"""
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from core.bank_engine import BankEngine
from core.models import Account, Transaction, TransactionType, TransactionStatus
from performance.benchmarks import (
    benchmark_searching,
    benchmark_sorting,
    plot_search_benchmark,
    plot_sort_benchmark
)


class BankApp(tk.Tk):
    """Main Tkinter Application window."""
    def __init__(self):
        super().__init__()
        self.title("BankFlow | Efficient Bank Transaction Processing System (DSA)")
        self.geometry("1200x820")
        self.minsize(1050, 720)

        # Initialize BankEngine
        self.engine = BankEngine()
        # Preload initial demo dataset
        self.engine.seed_demo_data()

        # Canvas reference for performance plots
        self.current_plot_canvas: Optional[FigureCanvasTkAgg] = None

        # Setup styles and build UI
        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    def _setup_styles(self):
        """Configure ttk styling for a clean, modern look."""
        self.configure(bg="#0b1329")
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure colors
        bg_dark = "#0b1329"
        card_bg = "#162032"
        text_light = "#f8fafc"
        accent_blue = "#0284c7"

        self.style.configure(".", background=bg_dark, foreground=text_light, font=("Segoe UI", 10))
        self.style.configure("TNotebook", background=bg_dark, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background="#1e293b",
            foreground="#cbd5e1",
            padding=[16, 8],
            font=("Segoe UI", 10, "bold")
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", accent_blue)],
            foreground=[("selected", "#ffffff")]
        )

        self.style.configure(
            "Card.TFrame",
            background=card_bg,
            relief="solid",
            borderwidth=1
        )
        self.style.configure("TLabel", background=bg_dark, foreground=text_light)
        self.style.configure("Card.TLabel", background=card_bg, foreground=text_light)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#38bdf8")
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 11, "bold"), foreground="#94a3b8")
        self.style.configure("StatNum.TLabel", font=("Segoe UI", 20, "bold"), foreground="#10b981", background=card_bg)
        self.style.configure("StatTitle.TLabel", font=("Segoe UI", 9), foreground="#94a3b8", background=card_bg)

        # Buttons
        self.style.configure(
            "Primary.TButton",
            background="#0284c7",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            borderwidth=0
        )
        self.style.map("Primary.TButton", background=[("active", "#0369a1")])

        self.style.configure(
            "Success.TButton",
            background="#10b981",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            borderwidth=0
        )
        self.style.map("Success.TButton", background=[("active", "#059669")])

        self.style.configure(
            "Warning.TButton",
            background="#f59e0b",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            borderwidth=0
        )
        self.style.map("Warning.TButton", background=[("active", "#d97706")])

        self.style.configure(
            "Danger.TButton",
            background="#ef4444",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            borderwidth=0
        )
        self.style.map("Danger.TButton", background=[("active", "#dc2626")])

        # Treeview styling
        self.style.configure(
            "Treeview",
            background="#111c2e",
            fieldbackground="#111c2e",
            foreground="#f1f5f9",
            rowheight=26,
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", "#0369a1")])

    def _build_ui(self):
        """Build the master application layout."""
        # Top Header Bar
        header_frame = tk.Frame(self, bg="#0e172a", height=65, padx=20, pady=12)
        header_frame.pack(fill="x", side="top")

        brand_lbl = tk.Label(
            header_frame,
            text="◈ BANKFLOW",
            font=("Segoe UI", 17, "bold"),
            fg="#38bdf8",
            bg="#0e172a"
        )
        brand_lbl.pack(side="left")

        subbrand_lbl = tk.Label(
            header_frame,
            text=" |  Efficient Bank Transaction Processing System (DSA)",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0e172a"
        )
        subbrand_lbl.pack(side="left", padx=5)

        reload_btn = ttk.Button(
            header_frame,
            text="↺ Reset Demo Data",
            style="Warning.TButton",
            command=self._on_reload_demo
        )
        reload_btn.pack(side="right", padx=6)

        # Tabbed Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        # 1. Dashboard Tab
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        self._build_dashboard_tab()

        # 2. Account Management (Hash Table)
        self.tab_accounts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_accounts, text="👤 Accounts (Hash Table)")
        self._build_accounts_tab()

        # 3. Transaction Processing (Queues)
        self.tab_transactions = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_transactions, text="⚡ Queues & Execution")
        self._build_transactions_tab()

        # 4. History & Mini-Statements (DLL & Stack)
        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text="📜 History & Undo")
        self._build_history_tab()

        # 5. Date-Range Queries (AVL Tree)
        self.tab_avl = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_avl, text="🌲 Date Range (AVL Tree)")
        self._build_avl_tab()

        # 6. Sorting & Search Demo
        self.tab_algorithms = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_algorithms, text="🔍 Sort & Search Demos")
        self._build_algorithms_tab()

        # 7. Graph Analysis (BFS & DFS)
        self.tab_graph = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_graph, text="🕸️ Fraud Graph (BFS/DFS)")
        self._build_graph_tab()

        # 8. Performance Benchmark Dashboard
        self.tab_perf = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_perf, text="📈 Performance Benchmarks")
        self._build_performance_tab()

        # Bottom Status Notification Bar
        self.status_bar = tk.Label(
            self,
            text="System Initialized. Demo data loaded with 8 accounts and pre-queued transactions.",
            bg="#0f172a",
            fg="#38bdf8",
            font=("Segoe UI", 9),
            anchor="w",
            padx=15,
            pady=6
        )
        self.status_bar.pack(fill="x", side="bottom")

    def log_status(self, message: str, is_error: bool = False):
        """Update bottom status message."""
        color = "#ef4444" if is_error else "#38bdf8"
        self.status_bar.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] {message}", fg=color)

    # =========================================================================
    # TAB 1: DASHBOARD
    # =========================================================================
    def _build_dashboard_tab(self):
        container = tk.Frame(self.tab_dashboard, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Stat cards row
        stats_frame = tk.Frame(container, bg="#0b1329")
        stats_frame.pack(fill="x", pady=(0, 15))

        self.stat_cards = {}
        cards_config = [
            ("total_accounts", "TOTAL ACCOUNTS", "Hash Table (Separate Chaining)", "#38bdf8"),
            ("total_balance", "BANK BALANCE", "Sum of Active Deposits", "#10b981"),
            ("reg_queue", "PENDING REGULAR", "Circular FIFO Queue", "#f59e0b"),
            ("pri_queue", "PENDING PRIORITY", "Binary Min-Heap (Due Time)", "#a855f7"),
            ("history_count", "TOTAL TRANSACTIONS", "Doubly Linked List", "#06b6d4"),
            ("undo_depth", "UNDO STACK DEPTH", "LIFO Transaction Stack", "#ec4899"),
        ]

        for i, (key, title, subtitle, color) in enumerate(cards_config):
            card = tk.Frame(stats_frame, bg="#162032", highlightbackground="#25334d", highlightthickness=1, padx=12, pady=10)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#94a3b8", bg="#162032")
            t_lbl.pack(anchor="w")

            val_lbl = tk.Label(card, text="0", font=("Segoe UI", 16, "bold"), fg=color, bg="#162032")
            val_lbl.pack(anchor="w", pady=2)

            sub_lbl = tk.Label(card, text=subtitle, font=("Segoe UI", 7), fg="#64748b", bg="#162032")
            sub_lbl.pack(anchor="w")

            self.stat_cards[key] = val_lbl

        # Quick Control Panel
        quick_frame = tk.LabelFrame(container, text=" Quick Control Station ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=12)
        quick_frame.pack(fill="x", pady=10)

        btn_row = tk.Frame(quick_frame, bg="#162032")
        btn_row.pack(fill="x")

        ttk.Button(btn_row, text="▶ Process Next Regular (FIFO)", style="Primary.TButton", command=self._on_process_regular).pack(side="left", padx=5)
        ttk.Button(btn_row, text="⭐ Process Next Priority (Min-Heap)", style="Warning.TButton", command=self._on_process_priority).pack(side="left", padx=5)
        ttk.Button(btn_row, text="⚡ Process All Queued", style="Success.TButton", command=self._on_process_all).pack(side="left", padx=5)
        ttk.Button(btn_row, text="↩ Undo Last Transaction (Stack)", style="Danger.TButton", command=self._on_undo_transaction).pack(side="left", padx=5)

        # Overview Data Structures Information Panel
        info_frame = tk.LabelFrame(container, text=" Architecture & Data Structure Integration Mapping ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=12)
        info_frame.pack(fill="both", expand=True, pady=10)

        arch_text = (
            "◈ Hash Table: Stores accounts by Account Number with custom polynomial rolling hash, separate chaining buckets, and dynamic resizing at λ > 0.75.\n"
            "◈ Circular Queue: Processes regular retail transactions in strictly chronological FIFO order with front & rear modular indexing.\n"
            "◈ Binary Min-Heap: Schedules urgent/priority transactions by due time, bubbling up high-priority settlements in O(log N) time.\n"
            "◈ Doubly Linked List: Maintains complete audit history with O(1) appends and bidirectional traversal for instant mini-statements.\n"
            "◈ LIFO Stack: Enables safe one-click transaction rollback/undo, reversing ledger balances atomically while checking funds.\n"
            "◈ AVL Tree: Self-balancing BST indexed by datetime for logarithmic range searches (O(log N + K)) across statements.\n"
            "◈ Merge Sort & Quick Sort: Manual recursive sorting algorithms comparing amount and date ordering efficiency.\n"
            "◈ Adjacency-List Graph: Models accounts as vertices and fund transfers as directed edges; BFS checks hops, DFS flags circular loops."
        )
        info_lbl = tk.Label(info_frame, text=arch_text, font=("Consolas", 9), fg="#cbd5e1", bg="#162032", justify="left")
        info_lbl.pack(anchor="nw", fill="both", expand=True)

    # =========================================================================
    # TAB 2: ACCOUNT MANAGEMENT (HASH TABLE)
    # =========================================================================
    def _build_accounts_tab(self):
        container = tk.Frame(self.tab_accounts, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        left_pane = tk.Frame(container, bg="#0b1329", width=380)
        left_pane.pack(side="left", fill="y", padx=(0, 15))

        # Create Account Form
        form_frame = tk.LabelFrame(left_pane, text=" Create Bank Account ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        form_frame.pack(fill="x", pady=(0, 12))

        tk.Label(form_frame, text="Account Number (digits):", bg="#162032", fg="#94a3b8").pack(anchor="w")
        self.entry_acc_num = ttk.Entry(form_frame)
        self.entry_acc_num.pack(fill="x", pady=(2, 8))

        tk.Label(form_frame, text="Customer Full Name:", bg="#162032", fg="#94a3b8").pack(anchor="w")
        self.entry_acc_name = ttk.Entry(form_frame)
        self.entry_acc_name.pack(fill="x", pady=(2, 8))

        tk.Label(form_frame, text="Opening Balance (₹):", bg="#162032", fg="#94a3b8").pack(anchor="w")
        self.entry_acc_bal = ttk.Entry(form_frame)
        self.entry_acc_bal.insert(0, "1000.00")
        self.entry_acc_bal.pack(fill="x", pady=(2, 12))

        ttk.Button(form_frame, text="+ Create Account", style="Success.TButton", command=self._on_create_account).pack(fill="x")

        # Hash Table Inspector Card
        ht_frame = tk.LabelFrame(left_pane, text=" Hash Table Inspector (Chaining) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        ht_frame.pack(fill="x")

        self.lbl_ht_stats = tk.Label(ht_frame, text="Loading hash table stats...", font=("Consolas", 8), bg="#162032", fg="#cbd5e1", justify="left")
        self.lbl_ht_stats.pack(anchor="w")

        # Right Pane: Account Directory Table & Search Comparison
        right_pane = tk.Frame(container, bg="#0b1329")
        right_pane.pack(side="right", fill="both", expand=True)

        # Search Bar with comparison
        search_frame = tk.Frame(right_pane, bg="#162032", padx=10, pady=8)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Search Account:", bg="#162032", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        self.entry_search_acc = ttk.Entry(search_frame, width=15)
        self.entry_search_acc.pack(side="left", padx=5)

        ttk.Button(search_frame, text="⚡ Compare Lookup Algorithms", style="Primary.TButton", command=self._on_compare_lookup).pack(side="left", padx=10)

        # Lookup result banner
        self.lbl_lookup_result = tk.Label(search_frame, text="Enter account number to compare Linear vs Binary vs Hash lookup.", bg="#162032", fg="#38bdf8", font=("Consolas", 8))
        self.lbl_lookup_result.pack(side="left", padx=10)

        # Accounts Treeview
        tbl_frame = tk.Frame(right_pane, bg="#0b1329")
        tbl_frame.pack(fill="both", expand=True)

        cols = ("acc_num", "name", "balance", "created")
        self.tree_accounts = ttk.Treeview(tbl_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_accounts.heading("acc_num", text="Account No.")
        self.tree_accounts.heading("name", text="Customer Name")
        self.tree_accounts.heading("balance", text="Balance (₹)")
        self.tree_accounts.heading("created", text="Created On")

        self.tree_accounts.column("acc_num", width=120, anchor="center")
        self.tree_accounts.column("name", width=200, anchor="w")
        self.tree_accounts.column("balance", width=140, anchor="e")
        self.tree_accounts.column("created", width=160, anchor="center")

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_accounts.python_command if hasattr(self.tree_accounts, 'python_command') else self.tree_accounts.yview)
        self.tree_accounts.configure(yscrollcommand=scroll_y.set)

        self.tree_accounts.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # =========================================================================
    # TAB 3: TRANSACTION PROCESSING & QUEUES
    # =========================================================================
    def _build_transactions_tab(self):
        container = tk.Frame(self.tab_transactions, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        top_pane = tk.Frame(container, bg="#0b1329")
        top_pane.pack(fill="x", pady=(0, 15))

        # Panel 1: Queue Regular Transaction (Circular Queue FIFO)
        q_reg_frame = tk.LabelFrame(top_pane, text=" Queue Regular (Circular FIFO Queue) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        q_reg_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.tx_reg_type = ttk.Combobox(q_reg_frame, values=["DEPOSIT", "WITHDRAWAL", "TRANSFER"], state="readonly")
        self.tx_reg_type.set("TRANSFER")
        self.tx_reg_type.pack(fill="x", pady=2)
        self.tx_reg_type.bind("<<ComboboxSelected>>", self._on_tx_type_change_reg)

        tk.Label(q_reg_frame, text="From Account:", bg="#162032", fg="#94a3b8").pack(anchor="w", pady=(4, 0))
        self.tx_reg_from = ttk.Entry(q_reg_frame)
        self.tx_reg_from.insert(0, "101")
        self.tx_reg_from.pack(fill="x", pady=2)

        tk.Label(q_reg_frame, text="To Account (for Transfers):", bg="#162032", fg="#94a3b8").pack(anchor="w", pady=(4, 0))
        self.tx_reg_to = ttk.Entry(q_reg_frame)
        self.tx_reg_to.insert(0, "102")
        self.tx_reg_to.pack(fill="x", pady=2)

        tk.Label(q_reg_frame, text="Amount (₹):", bg="#162032", fg="#94a3b8").pack(anchor="w", pady=(4, 0))
        self.tx_reg_amount = ttk.Entry(q_reg_frame)
        self.tx_reg_amount.insert(0, "1500.00")
        self.tx_reg_amount.pack(fill="x", pady=2)

        ttk.Button(q_reg_frame, text="+ Queue in Circular Queue", style="Primary.TButton", command=self._on_enqueue_regular).pack(fill="x", pady=(8, 0))

        # Panel 2: Schedule Priority Transaction (Min-Heap by Due Time)
        q_pri_frame = tk.LabelFrame(top_pane, text=" Schedule Priority (Min-Heap Due Time) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        q_pri_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self.tx_pri_type = ttk.Combobox(q_pri_frame, values=["DEPOSIT", "WITHDRAWAL", "TRANSFER"], state="readonly")
        self.tx_pri_type.set("TRANSFER")
        self.tx_pri_type.pack(fill="x", pady=2)

        tk.Label(q_pri_frame, text="From Account:", bg="#162032", fg="#94a3b8").pack(anchor="w", pady=(4, 0))
        self.tx_pri_from = ttk.Entry(q_pri_frame)
        self.tx_pri_from.insert(0, "107")
        self.tx_pri_from.pack(fill="x", pady=2)

        tk.Label(q_pri_frame, text="To Account (for Transfers):", bg="#162032", fg="#94a3b8").pack(anchor="w", pady=(4, 0))
        self.tx_pri_to = ttk.Entry(q_pri_frame)
        self.tx_pri_to.insert(0, "108")
        self.tx_pri_to.pack(fill="x", pady=2)

        amt_due_row = tk.Frame(q_pri_frame, bg="#162032")
        amt_due_row.pack(fill="x", pady=2)

        tk.Label(amt_due_row, text="Amount (₹):", bg="#162032", fg="#94a3b8").grid(row=0, column=0, sticky="w")
        tk.Label(amt_due_row, text="Due In (Mins):", bg="#162032", fg="#94a3b8").grid(row=0, column=1, sticky="w", padx=5)

        self.tx_pri_amount = ttk.Entry(amt_due_row)
        self.tx_pri_amount.insert(0, "5000.00")
        self.tx_pri_amount.grid(row=1, column=0, sticky="ew")

        self.tx_pri_mins = ttk.Entry(amt_due_row)
        self.tx_pri_mins.insert(0, "10")
        self.tx_pri_mins.grid(row=1, column=1, sticky="ew", padx=5)
        amt_due_row.grid_columnconfigure(0, weight=1)
        amt_due_row.grid_columnconfigure(1, weight=1)

        ttk.Button(q_pri_frame, text="⭐ Schedule in Min-Heap", style="Warning.TButton", command=self._on_enqueue_priority).pack(fill="x", pady=(8, 0))

        # Bottom Pane: Tables showing current queues
        bot_pane = tk.Frame(container, bg="#0b1329")
        bot_pane.pack(fill="both", expand=True)

        # Circular Queue Table
        reg_tbl_frame = tk.LabelFrame(bot_pane, text=" Circular Queue (FIFO Order) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        reg_tbl_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        cols = ("id", "type", "from", "to", "amt")
        self.tree_reg_queue = ttk.Treeview(reg_tbl_frame, columns=cols, show="headings")
        self.tree_reg_queue.heading("id", text="Tx ID")
        self.tree_reg_queue.heading("type", text="Type")
        self.tree_reg_queue.heading("from", text="From")
        self.tree_reg_queue.heading("to", text="To")
        self.tree_reg_queue.heading("amt", text="Amount (₹)")

        self.tree_reg_queue.column("id", width=80, anchor="center")
        self.tree_reg_queue.column("type", width=90, anchor="center")
        self.tree_reg_queue.column("from", width=60, anchor="center")
        self.tree_reg_queue.column("to", width=60, anchor="center")
        self.tree_reg_queue.column("amt", width=90, anchor="e")
        self.tree_reg_queue.pack(fill="both", expand=True)

        ttk.Button(reg_tbl_frame, text="▶ Process Front Regular", style="Primary.TButton", command=self._on_process_regular).pack(fill="x", pady=(5, 0))

        # Priority Min-Heap Table
        pri_tbl_frame = tk.LabelFrame(bot_pane, text=" Priority Min-Heap (Earliest Due Time First) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        pri_tbl_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))

        cols_pri = ("id", "type", "from", "to", "amt", "due")
        self.tree_pri_queue = ttk.Treeview(pri_tbl_frame, columns=cols_pri, show="headings")
        self.tree_pri_queue.heading("id", text="Tx ID")
        self.tree_pri_queue.heading("type", text="Type")
        self.tree_pri_queue.heading("from", text="From")
        self.tree_pri_queue.heading("to", text="To")
        self.tree_pri_queue.heading("amt", text="Amount (₹)")
        self.tree_pri_queue.heading("due", text="Due Time")

        self.tree_pri_queue.column("id", width=80, anchor="center")
        self.tree_pri_queue.column("type", width=80, anchor="center")
        self.tree_pri_queue.column("from", width=50, anchor="center")
        self.tree_pri_queue.column("to", width=50, anchor="center")
        self.tree_pri_queue.column("amt", width=80, anchor="e")
        self.tree_pri_queue.column("due", width=90, anchor="center")
        self.tree_pri_queue.pack(fill="both", expand=True)

        ttk.Button(pri_tbl_frame, text="⭐ Process Earliest Priority", style="Warning.TButton", command=self._on_process_priority).pack(fill="x", pady=(5, 0))

    def _on_tx_type_change_reg(self, event=None):
        """Enable or disable To field based on transaction type."""
        t = self.tx_reg_type.get()
        if t == "TRANSFER":
            self.tx_reg_to.config(state="normal")
        else:
            self.tx_reg_to.delete(0, tk.END)
            self.tx_reg_to.config(state="disabled")

    # =========================================================================
    # TAB 4: HISTORY & MINI-STATEMENTS (DLL & STACK)
    # =========================================================================
    def _build_history_tab(self):
        container = tk.Frame(self.tab_history, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        top_bar = tk.Frame(container, bg="#162032", padx=12, pady=10)
        top_bar.pack(fill="x", pady=(0, 12))

        # Mini-statement section
        tk.Label(top_bar, text="Mini-Statement for Account:", bg="#162032", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        self.entry_mini_acc = ttk.Entry(top_bar, width=12)
        self.entry_mini_acc.insert(0, "101")
        self.entry_mini_acc.pack(side="left", padx=5)

        tk.Label(top_bar, text="Last N:", bg="#162032", fg="#94a3b8").pack(side="left", padx=(10, 5))
        self.spin_mini_n = ttk.Spinbox(top_bar, from_=1, to=50, width=5)
        self.spin_mini_n.set("5")
        self.spin_mini_n.pack(side="left", padx=5)

        ttk.Button(top_bar, text="📜 Generate Mini-Statement (DLL)", style="Primary.TButton", command=self._on_generate_mini_statement).pack(side="left", padx=10)

        # Full history controls
        ttk.Button(top_bar, text="Show All History", style="Primary.TButton", command=self.populate_history_table).pack(side="left", padx=5)
        ttk.Button(top_bar, text="↩ Undo Most Recent (Stack)", style="Danger.TButton", command=self._on_undo_transaction).pack(side="right", padx=5)

        # History Treeview
        tbl_frame = tk.Frame(container, bg="#0b1329")
        tbl_frame.pack(fill="both", expand=True)

        cols = ("tx_id", "type", "from", "to", "amount", "status", "timestamp", "desc")
        self.tree_history = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        self.tree_history.heading("tx_id", text="Tx ID")
        self.tree_history.heading("type", text="Type")
        self.tree_history.heading("from", text="From")
        self.tree_history.heading("to", text="To")
        self.tree_history.heading("amount", text="Amount (₹)")
        self.tree_history.heading("status", text="Status")
        self.tree_history.heading("timestamp", text="Timestamp")
        self.tree_history.heading("desc", text="Description / Failure Reason")

        self.tree_history.column("tx_id", width=90, anchor="center")
        self.tree_history.column("type", width=100, anchor="center")
        self.tree_history.column("from", width=70, anchor="center")
        self.tree_history.column("to", width=70, anchor="center")
        self.tree_history.column("amount", width=110, anchor="e")
        self.tree_history.column("status", width=90, anchor="center")
        self.tree_history.column("timestamp", width=150, anchor="center")
        self.tree_history.column("desc", width=260, anchor="w")

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scroll_y.set)

        self.tree_history.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # =========================================================================
    # TAB 5: DATE-RANGE REPORTING (AVL TREE)
    # =========================================================================
    def _build_avl_tab(self):
        container = tk.Frame(self.tab_avl, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        header_frame = tk.Frame(container, bg="#162032", padx=15, pady=12)
        header_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            header_frame,
            text="🌲 AVL Tree Date-Range Query Engine",
            font=("Segoe UI", 12, "bold"),
            fg="#38bdf8",
            bg="#162032"
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="All transactions are indexed in a self-balancing AVL Tree by timestamp. Balance factor |h(L) - h(R)| <= 1 ensures O(log N + K) range queries.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#162032"
        ).pack(anchor="w", pady=(2, 8))

        # Inputs row
        inputs_row = tk.Frame(header_frame, bg="#162032")
        inputs_row.pack(fill="x")

        tk.Label(inputs_row, text="Start Hours Ago:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=5)
        self.entry_avl_start_hr = ttk.Entry(inputs_row, width=6)
        self.entry_avl_start_hr.insert(0, "6")
        self.entry_avl_start_hr.pack(side="left", padx=5)

        tk.Label(inputs_row, text="End Hours Ago:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=(12, 5))
        self.entry_avl_end_hr = ttk.Entry(inputs_row, width=6)
        self.entry_avl_end_hr.insert(0, "0")
        self.entry_avl_end_hr.pack(side="left", padx=5)

        ttk.Button(inputs_row, text="🔍 Query Range via AVL Tree", style="Primary.TButton", command=self._on_query_avl_range).pack(side="left", padx=15)

        self.lbl_avl_tree_stats = tk.Label(inputs_row, text="", font=("Consolas", 9), fg="#10b981", bg="#162032")
        self.lbl_avl_tree_stats.pack(side="right", padx=10)

        # AVL Results Treeview
        tbl_frame = tk.Frame(container, bg="#0b1329")
        tbl_frame.pack(fill="both", expand=True)

        cols = ("tx_id", "timestamp", "type", "from", "to", "amount", "status")
        self.tree_avl = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        self.tree_avl.heading("tx_id", text="Tx ID")
        self.tree_avl.heading("timestamp", text="Timestamp")
        self.tree_avl.heading("type", text="Type")
        self.tree_avl.heading("from", text="From")
        self.tree_avl.heading("to", text="To")
        self.tree_avl.heading("amount", text="Amount (₹)")
        self.tree_avl.heading("status", text="Status")

        self.tree_avl.column("tx_id", width=100, anchor="center")
        self.tree_avl.column("timestamp", width=160, anchor="center")
        self.tree_avl.column("type", width=100, anchor="center")
        self.tree_avl.column("from", width=80, anchor="center")
        self.tree_avl.column("to", width=80, anchor="center")
        self.tree_avl.column("amount", width=120, anchor="e")
        self.tree_avl.column("status", width=100, anchor="center")

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_avl.yview)
        self.tree_avl.configure(yscrollcommand=scroll_y.set)

        self.tree_avl.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # =========================================================================
    # TAB 6: SORTING & SEARCHING DEMONSTRATIONS
    # =========================================================================
    def _build_algorithms_tab(self):
        container = tk.Frame(self.tab_algorithms, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Top Control Row
        sort_control = tk.LabelFrame(container, text=" Manual Sorting Engine (Merge Sort vs Quick Sort) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=10)
        sort_control.pack(fill="x", pady=(0, 12))

        ctrl_row = tk.Frame(sort_control, bg="#162032")
        ctrl_row.pack(fill="x")

        tk.Label(ctrl_row, text="Sort By:", bg="#162032", fg="#94a3b8").pack(side="left", padx=5)
        self.combo_sort_by = ttk.Combobox(ctrl_row, values=["amount", "date"], state="readonly", width=10)
        self.combo_sort_by.set("amount")
        self.combo_sort_by.pack(side="left", padx=5)

        tk.Label(ctrl_row, text="Order:", bg="#162032", fg="#94a3b8").pack(side="left", padx=(10, 5))
        self.combo_sort_order = ttk.Combobox(ctrl_row, values=["Ascending", "Descending"], state="readonly", width=12)
        self.combo_sort_order.set("Descending")
        self.combo_sort_order.pack(side="left", padx=5)

        ttk.Button(ctrl_row, text="⚡ Run Merge Sort", style="Primary.TButton", command=lambda: self._on_run_sort("merge")).pack(side="left", padx=8)
        ttk.Button(ctrl_row, text="⚡ Run Quick Sort", style="Success.TButton", command=lambda: self._on_run_sort("quick")).pack(side="left", padx=8)

        self.lbl_sort_metrics = tk.Label(sort_control, text="Select options and run an algorithm to view comparison metrics.", font=("Consolas", 9), fg="#10b981", bg="#162032")
        self.lbl_sort_metrics.pack(anchor="w", pady=(8, 0))

        # Sorted Table
        tbl_frame = tk.Frame(container, bg="#0b1329")
        tbl_frame.pack(fill="both", expand=True)

        cols = ("tx_id", "amount", "timestamp", "type", "from", "to", "status")
        self.tree_sorted = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        self.tree_sorted.heading("tx_id", text="Tx ID")
        self.tree_sorted.heading("amount", text="Amount (₹)")
        self.tree_sorted.heading("timestamp", text="Timestamp")
        self.tree_sorted.heading("type", text="Type")
        self.tree_sorted.heading("from", text="From")
        self.tree_sorted.heading("to", text="To")
        self.tree_sorted.heading("status", text="Status")

        self.tree_sorted.column("tx_id", width=100, anchor="center")
        self.tree_sorted.column("amount", width=120, anchor="e")
        self.tree_sorted.column("timestamp", width=160, anchor="center")
        self.tree_sorted.column("type", width=100, anchor="center")
        self.tree_sorted.column("from", width=80, anchor="center")
        self.tree_sorted.column("to", width=80, anchor="center")
        self.tree_sorted.column("status", width=100, anchor="center")

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_sorted.yview)
        self.tree_sorted.configure(yscrollcommand=scroll_y.set)

        self.tree_sorted.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # =========================================================================
    # TAB 7: GRAPH-BASED FRAUD & NETWORK ANALYSIS (BFS & DFS)
    # =========================================================================
    def _build_graph_tab(self):
        container = tk.Frame(self.tab_graph, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Top Controls
        ctrl_frame = tk.LabelFrame(container, text=" Adjacency-List Graph Analysis Station ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=12)
        ctrl_frame.pack(fill="x", pady=(0, 15))

        row1 = tk.Frame(ctrl_frame, bg="#162032")
        row1.pack(fill="x", pady=4)

        tk.Label(row1, text="Start Account for BFS Exploration:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=5)
        self.entry_bfs_acc = ttk.Entry(row1, width=12)
        self.entry_bfs_acc.insert(0, "101")
        self.entry_bfs_acc.pack(side="left", padx=5)

        ttk.Button(row1, text="🌐 Run BFS Connected Accounts", style="Primary.TButton", command=self._on_run_bfs).pack(side="left", padx=10)

        ttk.Button(row1, text="🚨 Detect Circular Transfers (DFS Cycle Detection)", style="Danger.TButton", command=self._on_run_dfs_cycles).pack(side="right", padx=10)

        # Output Text/Treeview Split Pane
        split_pane = tk.PanedWindow(container, orient="horizontal", bg="#0b1329", sashwidth=4)
        split_pane.pack(fill="both", expand=True)

        # Left: Graph Transfers Edge Matrix
        left_box = tk.LabelFrame(split_pane, text=" Directed Transfer Edges in Graph ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        split_pane.add(left_box, minsize=350)

        cols_edge = ("from", "to", "amount", "tx_id")
        self.tree_edges = ttk.Treeview(left_box, columns=cols_edge, show="headings")
        self.tree_edges.heading("from", text="From")
        self.tree_edges.heading("to", text="To")
        self.tree_edges.heading("amount", text="Amount (₹)")
        self.tree_edges.heading("tx_id", text="Tx ID")

        self.tree_edges.column("from", width=70, anchor="center")
        self.tree_edges.column("to", width=70, anchor="center")
        self.tree_edges.column("amount", width=90, anchor="e")
        self.tree_edges.column("tx_id", width=80, anchor="center")
        self.tree_edges.pack(fill="both", expand=True)

        # Right: Fraud / BFS Diagnostic Output Log
        right_box = tk.LabelFrame(split_pane, text=" Graph Traversal & Fraud Detection Diagnostic Log ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        split_pane.add(right_box, minsize=450)

        self.txt_graph_log = tk.Text(right_box, bg="#0f172a", fg="#f1f5f9", font=("Consolas", 10), relief="flat", padx=10, pady=10)
        scroll_log = ttk.Scrollbar(right_box, orient="vertical", command=self.txt_graph_log.yview)
        self.txt_graph_log.configure(yscrollcommand=scroll_log.set)

        self.txt_graph_log.pack(side="left", fill="both", expand=True)
        scroll_log.pack(side="right", fill="y")

    # =========================================================================
    # TAB 8: PERFORMANCE ANALYSIS & MATPLOTLIB CHARTS
    # =========================================================================
    def _build_performance_tab(self):
        container = tk.Frame(self.tab_perf, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        ctrl_frame = tk.LabelFrame(container, text=" Synthetic Benchmark Generator & Visualizer ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=10)
        ctrl_frame.pack(fill="x", pady=(0, 10))

        row = tk.Frame(ctrl_frame, bg="#162032")
        row.pack(fill="x")

        tk.Label(row, text="Benchmark Suite:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=5)
        self.combo_bench_type = ttk.Combobox(row, values=["Search: Linear vs Binary vs Hash Table", "Sort: Merge Sort vs Quick Sort"], state="readonly", width=36)
        self.combo_bench_type.set("Search: Linear vs Binary vs Hash Table")
        self.combo_bench_type.pack(side="left", padx=5)

        tk.Label(row, text="Dataset Scale:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=(12, 5))
        self.combo_bench_scale = ttk.Combobox(row, values=["Standard (1k, 5k, 10k, 25k, 50k, 100k)", "Fast Demo (1k, 5k, 10k, 20k)"], state="readonly", width=32)
        self.combo_bench_scale.set("Fast Demo (1k, 5k, 10k, 20k)")
        self.combo_bench_scale.pack(side="left", padx=5)

        self.btn_run_bench = ttk.Button(row, text="📊 Run Benchmark & Plot", style="Success.TButton", command=self._on_run_benchmarks_threaded)
        self.btn_run_bench.pack(side="left", padx=15)

        self.lbl_bench_status = tk.Label(ctrl_frame, text="Ready. Click button above to generate synthetic data, measure perf_counter(), and render Matplotlib curves.", font=("Consolas", 9), fg="#94a3b8", bg="#162032")
        self.lbl_bench_status.pack(anchor="w", pady=(8, 0))

        # Chart Display Container Frame
        self.chart_container = tk.Frame(container, bg="#0f172a", highlightbackground="#1e293b", highlightthickness=1)
        self.chart_container.pack(fill="both", expand=True)

    # =========================================================================
    # EVENT HANDLERS & LOGIC BINDINGS
    # =========================================================================
    def _on_reload_demo(self):
        """Reset and reload rich sample demo dataset."""
        if messagebox.askyesno("Reset Demo Data", "Reset all banking data back to synthetic demo state?"):
            self.engine.seed_demo_data()
            self.refresh_all()
            self.log_status("Demo dataset successfully reloaded.")

    def _on_create_account(self):
        acc_num = self.entry_acc_num.get().strip()
        name = self.entry_acc_name.get().strip()
        try:
            bal = float(self.entry_acc_bal.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Opening balance must be a valid number.")
            return

        ok, msg = self.engine.create_account(acc_num, name, bal)
        if ok:
            messagebox.showinfo("Success", msg)
            self.entry_acc_num.delete(0, tk.END)
            self.entry_acc_name.delete(0, tk.END)
            self.refresh_all()
            self.log_status(msg)
        else:
            messagebox.showerror("Failed", msg)
            self.log_status(msg, is_error=True)

    def _on_compare_lookup(self):
        target = self.entry_search_acc.get().strip()
        if not target:
            messagebox.showwarning("Notice", "Please enter an account number to search.")
            return

        res = self.engine.compare_account_lookup(target)
        lin = res["linear"]
        bn = res["binary"]
        ht = res["hash"]

        found_str = "FOUND" if lin["found"] else "NOT FOUND"
        status_text = (
            f"Account {target}: {found_str} | "
            f"Linear {lin['complexity']}: {lin['comparisons']} comp, {lin['time_ms']:.4f}ms | "
            f"Binary {bn['complexity']}: {bn['comparisons']} comp, {bn['time_ms']:.4f}ms | "
            f"Hash {ht['complexity']}: {ht['comparisons']} comp, {ht['time_ms']:.4f}ms"
        )
        self.lbl_lookup_result.config(text=status_text)
        self.log_status(status_text)

    def _on_enqueue_regular(self):
        t_str = self.tx_reg_type.get()
        src = self.tx_reg_from.get().strip()
        dst = self.tx_reg_to.get().strip() if t_str == "TRANSFER" else None
        try:
            amt = float(self.tx_reg_amount.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        tx_type = TransactionType[t_str]
        ok, msg, tx = self.engine.queue_regular_transaction(tx_type, src, dst, amt, description="Regular queued transaction")
        if ok:
            self.refresh_all()
            self.log_status(msg)
        else:
            messagebox.showerror("Error", msg)
            self.log_status(msg, is_error=True)

    def _on_enqueue_priority(self):
        t_str = self.tx_pri_type.get()
        src = self.tx_pri_from.get().strip()
        dst = self.tx_pri_to.get().strip() if t_str == "TRANSFER" else None
        try:
            amt = float(self.tx_pri_amount.get().strip())
            mins = float(self.tx_pri_mins.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Amount and Due Minutes must be numbers.")
            return

        due_time = datetime.now() + timedelta(minutes=mins)
        tx_type = TransactionType[t_str]
        ok, msg, tx = self.engine.queue_priority_transaction(tx_type, src, dst, amt, due_time=due_time, description=f"Priority due in {mins}m")
        if ok:
            self.refresh_all()
            self.log_status(msg)
        else:
            messagebox.showerror("Error", msg)
            self.log_status(msg, is_error=True)

    def _on_process_regular(self):
        ok, msg, tx = self.engine.process_next_regular()
        self.refresh_all()
        if ok:
            self.log_status(f"[Circular Queue] {msg}")
        else:
            self.log_status(f"[Circular Queue] {msg}", is_error=True)

    def _on_process_priority(self):
        ok, msg, tx = self.engine.process_next_priority()
        self.refresh_all()
        if ok:
            self.log_status(f"[Min-Heap] {msg}")
        else:
            self.log_status(f"[Min-Heap] {msg}", is_error=True)

    def _on_process_all(self):
        count_ok, count_fail, logs = self.engine.process_all_queued()
        self.refresh_all()
        self.log_status(f"Batch Processing Completed: {count_ok} succeeded, {count_fail} failed.")

    def _on_undo_transaction(self):
        ok, msg, tx = self.engine.undo_last_transaction()
        self.refresh_all()
        if ok:
            messagebox.showinfo("Undo Successful", msg)
            self.log_status(msg)
        else:
            messagebox.showwarning("Undo Blocked", msg)
            self.log_status(msg, is_error=True)

    def _on_generate_mini_statement(self):
        acc = self.entry_mini_acc.get().strip()
        try:
            n = int(self.spin_mini_n.get().strip())
        except ValueError:
            n = 5

        records = self.engine.get_mini_statement(acc, limit=n)
        self.tree_history.delete(*self.tree_history.get_children())

        for r in records:
            d = r.to_dict()
            self.tree_history.insert(
                "",
                "end",
                values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["status"], d["timestamp"], d["description"] or d["failure_reason"])
            )
        self.log_status(f"Mini-statement for account {acc}: Displaying {len(records)} transactions (DLL backward traversal).")

    def _on_query_avl_range(self):
        try:
            start_hrs = float(self.entry_avl_start_hr.get().strip())
            end_hrs = float(self.entry_avl_end_hr.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Hours must be numbers.")
            return

        now = datetime.now()
        t_start = now - timedelta(hours=start_hrs)
        t_end = now - timedelta(hours=end_hrs)

        matches = self.engine.query_date_range(t_start, t_end)

        self.tree_avl.delete(*self.tree_avl.get_children())
        for m in matches:
            d = m.to_dict()
            self.tree_avl.insert(
                "",
                "end",
                values=(d["tx_id"], d["timestamp"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["status"])
            )

        tree_info = f"AVL Height: {self.engine.avl_index.get_height()} | Nodes: {self.engine.avl_index.total_nodes} | Range Matches: {len(matches)}"
        self.lbl_avl_tree_stats.config(text=tree_info)
        self.log_status(f"AVL Range Query returned {len(matches)} transactions. {tree_info}")

    def _on_run_sort(self, algo: str):
        sort_by = self.combo_sort_by.get()
        order = self.combo_sort_order.get()
        reverse = (order == "Descending")

        import time
        t0 = time.perf_counter()
        sorted_txs, comparisons = self.engine.sort_transactions(by=sort_by, algorithm=algo, reverse=reverse)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        self.tree_sorted.delete(*self.tree_sorted.get_children())
        for tx in sorted_txs:
            d = tx.to_dict()
            self.tree_sorted.insert(
                "",
                "end",
                values=(d["tx_id"], f"₹{d['amount']:,.2f}", d["timestamp"], d["type"], d["from_account"], d["to_account"], d["status"])
            )

        name = "Merge Sort" if algo == "merge" else "Quick Sort"
        metric_str = (
            f"Algorithm: {name} | Sorted {len(sorted_txs)} records by {sort_by} ({order}) | "
            f"Comparisons: {comparisons:,} | Execution Time: {elapsed_ms:.3f} ms | "
            f"Complexity: O(N log N)"
        )
        self.lbl_sort_metrics.config(text=metric_str)
        self.log_status(metric_str)

    def _on_run_bfs(self):
        acc = self.entry_bfs_acc.get().strip()
        connected = self.engine.get_connected_accounts_bfs(acc)

        self.txt_graph_log.delete("1.0", tk.END)
        self.txt_graph_log.insert(tk.END, f"=== BFS TRANSFER NETWORK EXPLORATION: ACCOUNT {acc} ===\n\n")

        if not connected:
            self.txt_graph_log.insert(tk.END, f"No outgoing fund transfer connections found for account {acc}.\n")
        else:
            self.txt_graph_log.insert(tk.END, f"Found {len(connected)} reachable accounts via transfer paths:\n\n")
            for item in connected:
                dest = item["account"]
                hops = item["hops"]
                path = item["path"]
                self.txt_graph_log.insert(tk.END, f"• Recipient: {dest} (Degree / Hops: {hops})\n")
                for p in path:
                    self.txt_graph_log.insert(tk.END, f"    └─ Tx {p['tx_id']}: ₹{p['amount']:,.2f} on {p['timestamp']}\n")
                self.txt_graph_log.insert(tk.END, "\n")

        self.log_status(f"BFS network trace for account {acc} completed. Reachable accounts: {len(connected)}")

    def _on_run_dfs_cycles(self):
        cycles = self.engine.detect_fraud_cycles_dfs()

        self.txt_graph_log.delete("1.0", tk.END)
        self.txt_graph_log.insert(tk.END, "=== SUSPICIOUS CIRCULAR TRANSFER DETECTION (DFS) ===\n\n")

        if not cycles:
            self.txt_graph_log.insert(tk.END, "✓ No circular transfer patterns (directed cycles) detected in current transfer graph.\n")
        else:
            self.txt_graph_log.insert(tk.END, f"⚠️ ALERT: Detected {len(cycles)} circular transfer pattern(s)!\n")
            self.txt_graph_log.insert(tk.END, "Circular transfers represent potential layering / money laundering transaction loops.\n\n")

            for idx, cycle in enumerate(cycles, 1):
                path_str = " ➔ ".join(cycle)
                self.txt_graph_log.insert(tk.END, f"[Loop #{idx}] {path_str}\n")
                # Show involved accounts
                self.txt_graph_log.insert(tk.END, f"   Participants: {', '.join(set(cycle))}\n\n")

        self.log_status(f"DFS Cycle Detection completed. Detected cycles: {len(cycles)}")

    def _on_run_benchmarks_threaded(self):
        """Run benchmarks in background thread to prevent UI freezing."""
        self.btn_run_bench.config(state="disabled")
        self.lbl_bench_status.config(text="Running benchmarks across synthetic datasets... Please wait a moment.", fg="#f59e0b")

        bench_choice = self.combo_bench_type.get()
        scale_choice = self.combo_bench_scale.get()

        if "Standard" in scale_choice:
            sizes = [1000, 5000, 10000, 25000, 50000, 100000]
        else:
            sizes = [1000, 5000, 10000, 20000]

        def _worker():
            try:
                if "Search" in bench_choice:
                    results = benchmark_searching(sizes)
                    fig = plot_search_benchmark(results)
                else:
                    sort_sizes = [s for s in sizes if s <= 25000]  # Cap for quick response
                    results = benchmark_sorting(sort_sizes)
                    fig = plot_sort_benchmark(results)

                self.after(0, lambda: self._display_benchmark_plot(fig))
            except Exception as e:
                self.after(0, lambda: self._benchmark_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _display_benchmark_plot(self, fig: plt.Figure):
        """Display Matplotlib figure in the Tkinter canvas."""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.current_plot_canvas = canvas

        self.btn_run_bench.config(state="normal")
        self.lbl_bench_status.config(text="✓ Benchmark completed successfully. Chart updated below.", fg="#10b981")
        self.log_status("Performance benchmark completed and plotted.")

    def _benchmark_error(self, err_msg: str):
        self.btn_run_bench.config(state="normal")
        self.lbl_bench_status.config(text=f"Benchmark error: {err_msg}", fg="#ef4444")
        self.log_status(f"Benchmark error: {err_msg}", is_error=True)

    # =========================================================================
    # REFRESH & POPULATE VIEWS
    # =========================================================================
    def refresh_all(self):
        """Update all tables, stat cards, and counters."""
        self.update_stat_cards()
        self.populate_accounts_table()
        self.populate_queue_tables()
        self.populate_history_table()
        self.populate_graph_table()

    def update_stat_cards(self):
        total_accounts = len(self.engine.get_all_accounts())
        total_balance = self.engine.get_total_bank_balance()
        reg_queue_len = self.engine.regular_queue.size()
        pri_queue_len = self.engine.priority_queue.size()
        history_len = self.engine.history.size()
        undo_depth = self.engine.undo_stack.size()

        self.stat_cards["total_accounts"].config(text=f"{total_accounts}")
        self.stat_cards["total_balance"].config(text=f"₹{total_balance:,.2f}")
        self.stat_cards["reg_queue"].config(text=f"{reg_queue_len}")
        self.stat_cards["pri_queue"].config(text=f"{pri_queue_len}")
        self.stat_cards["history_count"].config(text=f"{history_len}")
        self.stat_cards["undo_depth"].config(text=f"{undo_depth}")

        # Update Hash Table stats
        ht_stats = self.engine.accounts.bucket_collision_stats()
        stat_text = (
            f"Capacity: {ht_stats['capacity']}\n"
            f"Total Keys: {ht_stats['total_items']}\n"
            f"Load Factor (λ): {ht_stats['load_factor']} (Max: 0.75)\n"
            f"Non-empty Buckets: {ht_stats['non_empty_buckets']}\n"
            f"Colliding Buckets: {ht_stats['colliding_buckets']}\n"
            f"Max Chain Depth: {ht_stats['max_chain_length']}\n"
            f"Avg Chain Depth: {ht_stats['avg_chain_length']}\n"
            f"Dynamic Resizes: {ht_stats['resize_count']}"
        )
        self.lbl_ht_stats.config(text=stat_text)

    def populate_accounts_table(self):
        self.tree_accounts.delete(*self.tree_accounts.get_children())
        accounts = sorted(self.engine.get_all_accounts(), key=lambda a: a.account_number)
        for acc in accounts:
            d = acc.to_dict()
            self.tree_accounts.insert(
                "",
                "end",
                values=(d["account_number"], d["holder_name"], f"₹{d['balance']:,.2f}", d["created_at"])
            )

    def populate_queue_tables(self):
        # Regular Queue
        self.tree_reg_queue.delete(*self.tree_reg_queue.get_children())
        for tx in self.engine.regular_queue.to_list():
            d = tx.to_dict()
            self.tree_reg_queue.insert("", "end", values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}"))

        # Priority Min-Heap
        self.tree_pri_queue.delete(*self.tree_pri_queue.get_children())
        for tx in self.engine.priority_queue.to_sorted_list():
            d = tx.to_dict()
            self.tree_pri_queue.insert("", "end", values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["due_time"].split()[-1]))

    def populate_history_table(self):
        self.tree_history.delete(*self.tree_history.get_children())
        history = self.engine.get_all_history(newest_first=True)
        for tx in history:
            d = tx.to_dict()
            self.tree_history.insert(
                "",
                "end",
                values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["status"], d["timestamp"], d["description"] or d["failure_reason"])
            )

    def populate_graph_table(self):
        self.tree_edges.delete(*self.tree_edges.get_children())
        for from_acc, edges in self.engine.transfer_graph.adj_list.items():
            for e in edges:
                self.tree_edges.insert("", "end", values=(e.from_account, e.to_account, f"₹{e.amount:,.2f}", e.tx_id))


def launch():
    """Application launcher."""
    app = BankApp()
    app.mainloop()


if __name__ == "__main__":
    launch()
