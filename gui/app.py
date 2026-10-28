"""
BankFlow: Efficient Bank Transaction Processing System Using Data Structures and Algorithms
Desktop GUI Application powered by Tkinter and BankEngine.

Key Architectural Principles:
- Accounts: Hash Table (Separate Chaining, dynamic resizing > 0.75)
- Immediate Transactions: Atomic balance mutation + DLL recording + AVL index + Undo Stack
- Batch Processing: Circular Queue (FIFO)
- Priority Processing: Binary Min-Heap (Earliest Due Time)
- History & Mini-Statements: Doubly Linked List (Bidirectional traversal)
- Rollback & Undo: LIFO Stack
- Chronological Queries: AVL Tree (Self-balancing, O(log N + K) range query)
- Network Analysis & Fraud Detection: Directed Graph (BFS for reachability, DFS for cycles)
- Stable Sorting: Merge Sort (O(N log N) optimal)
"""
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import List, Optional

from core.bank_engine import BankEngine
from core.models import Account, Transaction, TransactionType, TransactionStatus


class BankApp(tk.Tk):
    """Main Application Window."""
    def __init__(self):
        super().__init__()
        self.title("BankFlow | Efficient Bank Transaction Processing System (DSA)")
        self.geometry("1240x840")
        self.minsize(1080, 740)

        # Initialize BankEngine with rich demo data
        self.engine = BankEngine()
        self.engine.seed_demo_data()

        # Setup styles and layout
        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    def _setup_styles(self):
        """Configure ttk styling for a clean, modern dark theme."""
        self.configure(bg="#0b1329")
        self.style = ttk.Style()
        self.style.theme_use("clam")

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

        self.style.configure("Card.TFrame", background=card_bg, relief="solid", borderwidth=1)
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
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=[12, 6]
        )
        self.style.map("Primary.TButton", background=[("active", "#0369a1")])

        self.style.configure(
            "Success.TButton",
            background="#10b981",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=[12, 6]
        )
        self.style.map("Success.TButton", background=[("active", "#059669")])

        self.style.configure(
            "Warning.TButton",
            background="#d97706",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=[12, 6]
        )
        self.style.map("Warning.TButton", background=[("active", "#b45309")])

        self.style.configure(
            "Danger.TButton",
            background="#dc2626",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=[12, 6]
        )
        self.style.map("Danger.TButton", background=[("active", "#b91c1c")])

        # Treeview (Tables)
        self.style.configure(
            "Treeview",
            background="#162032",
            foreground=text_light,
            fieldbackground="#162032",
            rowheight=26,
            font=("Consolas", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", "#0369a1")])

        # Input Fields
        input_bg = "#0f172a"
        border_col = "#334155"

        self.style.configure(
            "TEntry",
            fieldbackground=input_bg,
            foreground=text_light,
            insertcolor="#38bdf8",
            bordercolor=border_col,
            lightcolor=accent_blue,
            darkcolor=input_bg,
            padding=6
        )
        self.style.map(
            "TEntry",
            bordercolor=[("focus", "#38bdf8")],
            lightcolor=[("focus", "#38bdf8")],
            fieldbackground=[("disabled", "#1e293b"), ("readonly", "#1e293b")],
            foreground=[("disabled", "#64748b")]
        )

        self.style.configure(
            "TCombobox",
            fieldbackground=input_bg,
            foreground=text_light,
            background="#1e293b",
            arrowcolor="#38bdf8",
            bordercolor=border_col,
            padding=6
        )
        self.style.map(
            "TCombobox",
            bordercolor=[("focus", "#38bdf8")],
            lightcolor=[("focus", "#38bdf8")],
            fieldbackground=[("readonly", input_bg), ("focus", input_bg)],
            foreground=[("readonly", text_light), ("focus", text_light)]
        )

        self.option_add("*TCombobox*Listbox.background", input_bg)
        self.option_add("*TCombobox*Listbox.foreground", text_light)
        self.option_add("*TCombobox*Listbox.selectBackground", accent_blue)
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))
        self.option_add("*insertBackground", "#38bdf8")
        self.option_add("*insertWidth", "2")

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
            text=" |  Efficient Bank Transaction Processing System (DSA Engine)",
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

        # Tab 1: Dashboard
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        self._build_dashboard_tab()

        # Tab 2: Accounts (Hash Table O(1))
        self.tab_accounts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_accounts, text="👤 Accounts (Hash Table)")
        self._build_accounts_tab()

        # Tab 3: Transactions & Queues (Immediate + Queued)
        self.tab_transactions = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_transactions, text="⚡ Transactions & Queues")
        self._build_transactions_tab()

        # Tab 4: History & Undo (DLL & Stack)
        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text="📜 History & Undo")
        self._build_history_tab()

        # Tab 5: Date-Range (AVL Tree O(log N + K))
        self.tab_avl = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_avl, text="🌲 Date Range (AVL Tree)")
        self._build_avl_tab()

        # Tab 6: Fraud Graph (BFS & DFS)
        self.tab_graph = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_graph, text="🕸️ Fraud Graph (BFS/DFS)")
        self._build_graph_tab()

        # Bottom Status Bar
        self.status_bar = tk.Label(
            self,
            text="System Initialized. Ready for banking operations.",
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

        stats_frame = tk.Frame(container, bg="#0b1329")
        stats_frame.pack(fill="x", pady=(0, 15))

        self.stat_cards = {}
        cards_config = [
            ("total_accounts", "TOTAL ACCOUNTS", "Hash Table O(1)", "#38bdf8"),
            ("total_balance", "BANK BALANCE", "Active Ledger Sum", "#10b981"),
            ("reg_queue", "PENDING REGULAR", "Circular FIFO Queue", "#f59e0b"),
            ("pri_queue", "PENDING PRIORITY", "Binary Min-Heap", "#a855f7"),
            ("history_count", "TOTAL TRANSACTIONS", "Doubly Linked List", "#06b6d4"),
            ("undo_depth", "UNDO STACK DEPTH", "LIFO Reversible", "#ec4899"),
        ]

        for i, (key, title, subtitle, color) in enumerate(cards_config):
            card = tk.Frame(stats_frame, bg="#162032", relief="solid", borderwidth=1, padx=14, pady=12)
            card.grid(row=0, column=i, sticky="nsew", padx=4)
            stats_frame.grid_columnconfigure(i, weight=1)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#162032")
            t_lbl.pack(anchor="w")

            val_lbl = tk.Label(card, text="0", font=("Segoe UI", 18, "bold"), fg=color, bg="#162032")
            val_lbl.pack(anchor="w", pady=(3, 0))
            self.stat_cards[key] = val_lbl

            s_lbl = tk.Label(card, text=subtitle, font=("Segoe UI", 8), fg="#64748b", bg="#162032")
            s_lbl.pack(anchor="w")

        # Main Info & Shortcuts
        mid_pane = tk.Frame(container, bg="#0b1329")
        mid_pane.pack(fill="both", expand=True)

        # Left: Quick Actions
        qa_frame = tk.LabelFrame(mid_pane, text=" Quick Banking Actions ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        qa_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(qa_frame, text="Perform direct financial operations with instant ledger reflection:", bg="#162032", fg="#cbd5e1").pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(qa_frame, bg="#162032")
        btn_row.pack(fill="x", pady=5)

        ttk.Button(btn_row, text="⚡ New Transaction", style="Primary.TButton", command=lambda: self.notebook.select(self.tab_transactions)).pack(side="left", padx=5)
        ttk.Button(btn_row, text="👤 Create Account", style="Success.TButton", command=lambda: self.notebook.select(self.tab_accounts)).pack(side="left", padx=5)
        ttk.Button(btn_row, text="↩ Rollback Last Tx (Undo)", style="Danger.TButton", command=self._on_undo_transaction).pack(side="left", padx=5)

        # Right: DSA Engine Architecture
        info_frame = tk.LabelFrame(mid_pane, text=" DSA Architecture (No Redundant Comparisons) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        info_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        arch_text = (
            "◈ Hash Table (Separate Chaining): Stores customer accounts with O(1) average lookup & dynamic auto-resizing.\n"
            "◈ Doubly Linked List: Complete chronological audit trail with bidirectional traversal & O(1) appends.\n"
            "◈ LIFO Stack: Atomic transaction rollback & ledger reversal checking source and destination solvency.\n"
            "◈ AVL Tree: Self-balancing BST indexed by datetime; guarantees O(log N + K) chronological queries.\n"
            "◈ Binary Min-Heap: Priority transaction scheduling keyed by due time (O(log N) insert/extract).\n"
            "◈ Circular Queue: FIFO batch transaction queue with fixed capacity & wrap-around pointers (O(1)).\n"
            "◈ Directed Graph: Accounts as vertices, transfers as directed edges; BFS for money trail, DFS for cycle detection.\n"
            "◈ Merge Sort: Single optimal stable sorting algorithm (O(N log N)) for transaction history."
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
        self.entry_acc_num.pack(fill="x", pady=(2, 6))

        tk.Label(form_frame, text="Customer Full Name:", bg="#162032", fg="#94a3b8").pack(anchor="w")
        self.entry_acc_name = ttk.Entry(form_frame)
        self.entry_acc_name.pack(fill="x", pady=(2, 6))

        tk.Label(form_frame, text="Opening Balance (₹):", bg="#162032", fg="#94a3b8").pack(anchor="w")
        self.entry_acc_bal = ttk.Entry(form_frame)
        self.entry_acc_bal.insert(0, "5000.00")
        self.entry_acc_bal.pack(fill="x", pady=(2, 10))

        ttk.Button(form_frame, text="+ Create Account", style="Success.TButton", command=self._on_create_account).pack(fill="x")

        # Quick Actions on Selected Account
        qa_acc_frame = tk.LabelFrame(left_pane, text=" Quick Actions (Selected Account) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        qa_acc_frame.pack(fill="x", pady=(0, 12))

        tk.Label(qa_acc_frame, text="Select an account from the table, then execute:", bg="#162032", fg="#94a3b8", font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 8))

        btn_grid = tk.Frame(qa_acc_frame, bg="#162032")
        btn_grid.pack(fill="x")
        ttk.Button(btn_grid, text="➕ Quick Deposit", style="Success.TButton", command=self._on_quick_deposit).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(btn_grid, text="➖ Quick Withdraw", style="Warning.TButton", command=self._on_quick_withdraw).pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Hash Table Inspector Card
        ht_frame = tk.LabelFrame(left_pane, text=" Hash Table Inspector (Chaining) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        ht_frame.pack(fill="x")

        self.lbl_ht_stats = tk.Label(ht_frame, text="Loading hash table stats...", font=("Consolas", 8), bg="#162032", fg="#cbd5e1", justify="left")
        self.lbl_ht_stats.pack(anchor="w")

        # Right Pane: Account Directory & Instant Search
        right_pane = tk.Frame(container, bg="#0b1329")
        right_pane.pack(side="right", fill="both", expand=True)

        # Search Bar (Hash Table O(1) Lookup)
        search_frame = tk.Frame(right_pane, bg="#162032", padx=10, pady=8)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Search Account:", bg="#162032", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)
        self.entry_search_acc = ttk.Entry(search_frame, width=15)
        self.entry_search_acc.pack(side="left", padx=5)
        self.entry_search_acc.bind("<Return>", lambda e: self._on_search_account())

        ttk.Button(search_frame, text="🔍 Find (Hash O(1))", style="Primary.TButton", command=self._on_search_account).pack(side="left", padx=8)

        self.lbl_lookup_result = tk.Label(search_frame, text="Enter account number to look up in Hash Table O(1).", bg="#162032", fg="#38bdf8", font=("Consolas", 9))
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
        self.tree_accounts.column("name", width=220, anchor="w")
        self.tree_accounts.column("balance", width=150, anchor="e")
        self.tree_accounts.column("created", width=180, anchor="center")

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_accounts.yview)
        self.tree_accounts.configure(yscrollcommand=scroll_y.set)

        self.tree_accounts.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # =========================================================================
    # TAB 3: TRANSACTIONS & QUEUES
    # =========================================================================
    def _build_transactions_tab(self):
        container = tk.Frame(self.tab_transactions, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Top Pane: Two Sections - Instant Transaction vs Queuing
        top_pane = tk.Frame(container, bg="#0b1329")
        top_pane.pack(fill="x", pady=(0, 15))

        # Panel 1: INSTANT TRANSACTION EXECUTION (DIRECT REFLECTION)
        instant_frame = tk.LabelFrame(
            top_pane,
            text=" ⚡ Instant Transaction (Reflects Immediately) ",
            bg="#162032",
            fg="#10b981",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=12
        )
        instant_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        row1 = tk.Frame(instant_frame, bg="#162032")
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="Transaction Type:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.inst_tx_type = ttk.Combobox(row1, values=["DEPOSIT", "WITHDRAWAL", "TRANSFER"], state="readonly", width=14)
        self.inst_tx_type.set("TRANSFER")
        self.inst_tx_type.pack(side="right", fill="x", expand=True, padx=(8, 0))
        self.inst_tx_type.bind("<<ComboboxSelected>>", self._on_inst_type_change)

        row2 = tk.Frame(instant_frame, bg="#162032")
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="From Account:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.inst_from_acc = ttk.Combobox(row2, state="readonly", width=14)
        self.inst_from_acc.pack(side="right", fill="x", expand=True, padx=(8, 0))

        self.row_to = tk.Frame(instant_frame, bg="#162032")
        self.row_to.pack(fill="x", pady=2)
        tk.Label(self.row_to, text="To Account:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.inst_to_acc = ttk.Combobox(self.row_to, state="readonly", width=14)
        self.inst_to_acc.pack(side="right", fill="x", expand=True, padx=(8, 0))

        row3 = tk.Frame(instant_frame, bg="#162032")
        row3.pack(fill="x", pady=2)
        tk.Label(row3, text="Amount (₹):", bg="#162032", fg="#94a3b8").pack(side="left")
        self.inst_amount = ttk.Entry(row3)
        self.inst_amount.insert(0, "2500.00")
        self.inst_amount.pack(side="right", fill="x", expand=True, padx=(8, 0))

        row4 = tk.Frame(instant_frame, bg="#162032")
        row4.pack(fill="x", pady=2)
        tk.Label(row4, text="Description:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.inst_desc = ttk.Entry(row4)
        self.inst_desc.insert(0, "Direct Immediate Settlement")
        self.inst_desc.pack(side="right", fill="x", expand=True, padx=(8, 0))

        ttk.Button(
            instant_frame,
            text="⚡ Execute Transaction Now",
            style="Success.TButton",
            command=self._on_execute_instant
        ).pack(fill="x", pady=(10, 0))

        # Panel 2: QUEUED TRANSACTION ENGINE (Circular Queue & Min-Heap)
        queue_frame = tk.LabelFrame(
            top_pane,
            text=" ⏳ Batch & Priority Queuing (Deferred) ",
            bg="#162032",
            fg="#38bdf8",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=12
        )
        queue_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        qrow1 = tk.Frame(queue_frame, bg="#162032")
        qrow1.pack(fill="x", pady=2)
        tk.Label(qrow1, text="Queue Mode:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.q_mode = ttk.Combobox(qrow1, values=["Circular Queue (FIFO)", "Min-Heap (Priority Due Time)"], state="readonly")
        self.q_mode.set("Circular Queue (FIFO)")
        self.q_mode.pack(side="right", fill="x", expand=True, padx=(8, 0))

        qrow2 = tk.Frame(queue_frame, bg="#162032")
        qrow2.pack(fill="x", pady=2)
        tk.Label(qrow2, text="From Account:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.q_from_acc = ttk.Combobox(qrow2, state="readonly", width=14)
        self.q_from_acc.pack(side="right", fill="x", expand=True, padx=(8, 0))

        qrow3 = tk.Frame(queue_frame, bg="#162032")
        qrow3.pack(fill="x", pady=2)
        tk.Label(qrow3, text="To Account:", bg="#162032", fg="#94a3b8").pack(side="left")
        self.q_to_acc = ttk.Combobox(qrow3, state="readonly", width=14)
        self.q_to_acc.pack(side="right", fill="x", expand=True, padx=(8, 0))

        qrow4 = tk.Frame(queue_frame, bg="#162032")
        qrow4.pack(fill="x", pady=2)
        tk.Label(qrow4, text="Amount (₹):", bg="#162032", fg="#94a3b8").pack(side="left")
        self.q_amount = ttk.Entry(qrow4)
        self.q_amount.insert(0, "5000.00")
        self.q_amount.pack(side="right", fill="x", expand=True, padx=(8, 0))

        q_btn_row = tk.Frame(queue_frame, bg="#162032")
        q_btn_row.pack(fill="x", pady=(10, 0))

        ttk.Button(q_btn_row, text="+ Enqueue Transaction", style="Primary.TButton", command=self._on_enqueue_transaction).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(q_btn_row, text="⚡ Process All Queued", style="Warning.TButton", command=self._on_process_all).pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Bottom Pane: Tables showing current queues
        bot_pane = tk.Frame(container, bg="#0b1329")
        bot_pane.pack(fill="both", expand=True)

        # Circular Queue Table
        reg_tbl_frame = tk.LabelFrame(bot_pane, text=" Circular FIFO Queue (Regular Pending) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
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

    def _on_inst_type_change(self, event=None):
        t = self.inst_tx_type.get()
        if t == "TRANSFER":
            self.inst_to_acc.config(state="readonly")
        else:
            self.inst_to_acc.config(state="disabled")

    # =========================================================================
    # TAB 4: HISTORY & UNDO (DLL & STACK)
    # =========================================================================
    def _build_history_tab(self):
        container = tk.Frame(self.tab_history, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        top_bar = tk.Frame(container, bg="#162032", padx=12, pady=10)
        top_bar.pack(fill="x", pady=(0, 10))

        # Undo Section
        undo_subframe = tk.Frame(top_bar, bg="#162032")
        undo_subframe.pack(side="left")

        ttk.Button(undo_subframe, text="↩ Rollback / Undo Last Tx", style="Danger.TButton", command=self._on_undo_transaction).pack(side="left", padx=5)
        self.lbl_undo_info = tk.Label(undo_subframe, text="LIFO Stack ready for rollback.", bg="#162032", fg="#cbd5e1", font=("Segoe UI", 9))
        self.lbl_undo_info.pack(side="left", padx=8)

        # Mini-Statement Section
        stmt_subframe = tk.Frame(top_bar, bg="#162032")
        stmt_subframe.pack(side="right")

        tk.Label(stmt_subframe, text="Mini-Statement A/C:", bg="#162032", fg="#94a3b8").pack(side="left", padx=4)
        self.combo_stmt_acc = ttk.Combobox(stmt_subframe, state="readonly", width=10)
        self.combo_stmt_acc.pack(side="left", padx=4)

        ttk.Button(stmt_subframe, text="📄 View Mini-Statement", style="Primary.TButton", command=self._on_generate_mini_statement).pack(side="left", padx=6)

        # Sorting Controls (Merge Sort Only - Single Best Algorithm)
        sort_bar = tk.Frame(container, bg="#162032", padx=12, pady=8)
        sort_bar.pack(fill="x", pady=(0, 10))

        tk.Label(sort_bar, text="Sort History (Merge Sort O(N log N)):", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)

        tk.Label(sort_bar, text="Sort By:", bg="#162032", fg="#94a3b8").pack(side="left", padx=(10, 4))
        self.combo_sort_by = ttk.Combobox(sort_bar, values=["date", "amount"], state="readonly", width=10)
        self.combo_sort_by.set("date")
        self.combo_sort_by.pack(side="left", padx=4)

        tk.Label(sort_bar, text="Order:", bg="#162032", fg="#94a3b8").pack(side="left", padx=(10, 4))
        self.combo_sort_order = ttk.Combobox(sort_bar, values=["Descending (Newest / Highest)", "Ascending (Oldest / Lowest)"], state="readonly", width=28)
        self.combo_sort_order.set("Descending (Newest / Highest)")
        self.combo_sort_order.pack(side="left", padx=4)

        ttk.Button(sort_bar, text="Apply Sort", style="Primary.TButton", command=self._on_apply_sort).pack(side="left", padx=10)
        self.lbl_sort_metrics = tk.Label(sort_bar, text="", font=("Consolas", 9), fg="#10b981", bg="#162032")
        self.lbl_sort_metrics.pack(side="left", padx=10)

        # History Treeview
        tbl_frame = tk.Frame(container, bg="#0b1329")
        tbl_frame.pack(fill="both", expand=True)

        cols = ("id", "type", "from", "to", "amt", "status", "timestamp", "desc")
        self.tree_history = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        self.tree_history.heading("id", text="Tx ID")
        self.tree_history.heading("type", text="Type")
        self.tree_history.heading("from", text="From")
        self.tree_history.heading("to", text="To")
        self.tree_history.heading("amt", text="Amount (₹)")
        self.tree_history.heading("status", text="Status")
        self.tree_history.heading("timestamp", text="Timestamp")
        self.tree_history.heading("desc", text="Description / Details")

        self.tree_history.column("id", width=85, anchor="center")
        self.tree_history.column("type", width=95, anchor="center")
        self.tree_history.column("from", width=65, anchor="center")
        self.tree_history.column("to", width=65, anchor="center")
        self.tree_history.column("amt", width=110, anchor="e")
        self.tree_history.column("status", width=95, anchor="center")
        self.tree_history.column("timestamp", width=155, anchor="center")
        self.tree_history.column("desc", width=240, anchor="w")

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscrollcommand=scroll_y.set)

        self.tree_history.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # =========================================================================
    # TAB 5: DATE-RANGE QUERIES (AVL TREE)
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
            text="Every transaction is indexed in a balanced AVL Tree by timestamp. Strict balancing (|h(L) - h(R)| <= 1) guarantees O(log N + K) range lookups.",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#162032"
        ).pack(anchor="w", pady=(2, 8))

        inputs_row = tk.Frame(header_frame, bg="#162032")
        inputs_row.pack(fill="x")

        tk.Label(inputs_row, text="Start Hours Ago:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=5)
        self.entry_avl_start_hr = ttk.Entry(inputs_row, width=6)
        self.entry_avl_start_hr.insert(0, "24")
        self.entry_avl_start_hr.pack(side="left", padx=5)

        tk.Label(inputs_row, text="End Hours Ago:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=(12, 5))
        self.entry_avl_end_hr = ttk.Entry(inputs_row, width=6)
        self.entry_avl_end_hr.insert(0, "0")
        self.entry_avl_end_hr.pack(side="left", padx=5)

        ttk.Button(inputs_row, text="🔍 Query Range via AVL Tree", style="Primary.TButton", command=self._on_query_avl_range).pack(side="left", padx=12)
        ttk.Button(inputs_row, text="Last 6 Hours", style="Primary.TButton", command=lambda: self._set_avl_preset(6, 0)).pack(side="left", padx=3)
        ttk.Button(inputs_row, text="All Time", style="Primary.TButton", command=lambda: self._set_avl_preset(168, 0)).pack(side="left", padx=3)

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

    def _set_avl_preset(self, start_hrs: float, end_hrs: float):
        self.entry_avl_start_hr.delete(0, tk.END)
        self.entry_avl_start_hr.insert(0, str(start_hrs))
        self.entry_avl_end_hr.delete(0, tk.END)
        self.entry_avl_end_hr.insert(0, str(end_hrs))
        self._on_query_avl_range()

    # =========================================================================
    # TAB 6: FRAUD DETECTION & GRAPH ANALYSIS
    # =========================================================================
    def _build_graph_tab(self):
        container = tk.Frame(self.tab_graph, bg="#0b1329", padx=15, pady=15)
        container.pack(fill="both", expand=True)

        top_ctrl = tk.Frame(container, bg="#162032", padx=12, pady=10)
        top_ctrl.pack(fill="x", pady=(0, 12))

        # BFS Exploration
        tk.Label(top_ctrl, text="BFS Money Trail from A/C:", bg="#162032", fg="#cbd5e1").pack(side="left", padx=4)
        self.combo_bfs_start = ttk.Combobox(top_ctrl, state="readonly", width=10)
        self.combo_bfs_start.pack(side="left", padx=4)

        ttk.Button(top_ctrl, text="🔍 Run BFS Exploration", style="Primary.TButton", command=self._on_run_bfs).pack(side="left", padx=8)

        # DFS Cycle Detection
        ttk.Button(top_ctrl, text="🚨 Detect Fraud Cycles (DFS)", style="Danger.TButton", command=self._on_run_dfs_cycles).pack(side="right", padx=10)

        # Graph Results split pane
        body_pane = tk.Frame(container, bg="#0b1329")
        body_pane.pack(fill="both", expand=True)

        # Left: Transferred Edges
        edge_frame = tk.LabelFrame(body_pane, text=" Directed Transfer Edges (Adjacency List) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        edge_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        cols = ("from", "to", "amount", "tx_id")
        self.tree_edges = ttk.Treeview(edge_frame, columns=cols, show="headings")
        self.tree_edges.heading("from", text="From")
        self.tree_edges.heading("to", text="To")
        self.tree_edges.heading("amount", text="Amount (₹)")
        self.tree_edges.heading("tx_id", text="Tx ID")

        self.tree_edges.column("from", width=80, anchor="center")
        self.tree_edges.column("to", width=80, anchor="center")
        self.tree_edges.column("amount", width=100, anchor="e")
        self.tree_edges.column("tx_id", width=90, anchor="center")
        self.tree_edges.pack(fill="both", expand=True)

        # Right: Graph Analysis Output Log
        log_frame = tk.LabelFrame(body_pane, text=" Graph Analysis Results (BFS & DFS Findings) ", bg="#162032", fg="#38bdf8", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        log_frame.pack(side="right", fill="both", expand=True, padx=(6, 0))

        self.txt_graph_log = tk.Text(log_frame, bg="#0f172a", fg="#f8fafc", font=("Consolas", 10), insertbackground="#38bdf8", relief="flat", padx=10, pady=10)
        self.txt_graph_log.pack(fill="both", expand=True)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    def _on_reload_demo(self):
        if messagebox.askyesno("Reset Demo Data", "Reset all accounts and transactions back to initial demo state?"):
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

    def _on_search_account(self):
        target = self.entry_search_acc.get().strip()
        if not target:
            messagebox.showwarning("Notice", "Please enter an account number to search.")
            return

        acc = self.engine.get_account(target)
        if acc:
            status_text = f"FOUND in Hash Table O(1): A/C {acc.account_number} ({acc.holder_name}) - Balance: ₹{acc.balance:,.2f}"
            self.lbl_lookup_result.config(text=status_text, fg="#10b981")
            self.log_status(status_text)
            # Highlight in treeview
            for item in self.tree_accounts.get_children():
                vals = self.tree_accounts.item(item, "values")
                if vals and vals[0] == target:
                    self.tree_accounts.selection_set(item)
                    self.tree_accounts.see(item)
                    break
        else:
            status_text = f"NOT FOUND in Hash Table O(1): Account {target} does not exist."
            self.lbl_lookup_result.config(text=status_text, fg="#ef4444")
            self.log_status(status_text, is_error=True)

    def _on_quick_deposit(self):
        selected = self.tree_accounts.selection()
        if not selected:
            messagebox.showwarning("Select Account", "Please click on an account in the table first.")
            return

        vals = self.tree_accounts.item(selected[0], "values")
        acc_num = vals[0]
        amt_str = simpledialog.askstring("Quick Deposit", f"Deposit amount for Account {acc_num}:", initialvalue="5000.00")
        if not amt_str:
            return

        try:
            amt = float(amt_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a positive number.")
            return

        ok, msg, tx = self.engine.execute_immediate(
            TransactionType.DEPOSIT,
            from_account=acc_num,
            to_account=None,
            amount=amt,
            description="Branch Cash Deposit"
        )
        if ok:
            messagebox.showinfo("Deposit Success", msg)
            self.refresh_all()
            self.log_status(msg)
        else:
            messagebox.showerror("Deposit Failed", msg)
            self.log_status(msg, is_error=True)

    def _on_quick_withdraw(self):
        selected = self.tree_accounts.selection()
        if not selected:
            messagebox.showwarning("Select Account", "Please click on an account in the table first.")
            return

        vals = self.tree_accounts.item(selected[0], "values")
        acc_num = vals[0]
        amt_str = simpledialog.askstring("Quick Withdrawal", f"Withdrawal amount from Account {acc_num}:", initialvalue="2000.00")
        if not amt_str:
            return

        try:
            amt = float(amt_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a positive number.")
            return

        ok, msg, tx = self.engine.execute_immediate(
            TransactionType.WITHDRAWAL,
            from_account=acc_num,
            to_account=None,
            amount=amt,
            description="ATM Cash Withdrawal"
        )
        if ok:
            messagebox.showinfo("Withdrawal Success", msg)
            self.refresh_all()
            self.log_status(msg)
        else:
            messagebox.showerror("Withdrawal Failed", msg)
            self.log_status(msg, is_error=True)

    def _on_execute_instant(self):
        """Execute transaction immediately with instant balance reflection."""
        t_str = self.inst_tx_type.get()
        src = self.inst_from_acc.get().strip()
        dst = self.inst_to_acc.get().strip() if t_str == "TRANSFER" else None
        desc = self.inst_desc.get().strip() or "Instant Transaction"

        if not src:
            messagebox.showerror("Error", "Please select a source account.")
            return

        if t_str == "TRANSFER":
            if not dst:
                messagebox.showerror("Error", "Please select a destination account.")
                return
            if src == dst:
                messagebox.showerror("Error", "Source and destination accounts cannot be identical.")
                return

        try:
            amt = float(self.inst_amount.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        tx_type = TransactionType[t_str]
        ok, msg, tx = self.engine.execute_immediate(tx_type, src, dst, amt, description=desc)

        if ok:
            messagebox.showinfo("Transaction Complete", msg)
            self.refresh_all()
            self.log_status(f"✓ {msg}")
        else:
            messagebox.showerror("Transaction Failed", msg)
            self.log_status(f"✗ {msg}", is_error=True)

    def _on_enqueue_transaction(self):
        """Queue transaction into Circular Queue or Min-Heap."""
        mode = self.q_mode.get()
        src = self.q_from_acc.get().strip()
        dst = self.q_to_acc.get().strip()

        if not src:
            messagebox.showerror("Error", "Please select a source account.")
            return
        if not dst:
            messagebox.showerror("Error", "Please select a destination account.")
            return
        if src == dst:
            messagebox.showerror("Error", "Source and destination accounts cannot be identical.")
            return

        try:
            amt = float(self.q_amount.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        if "Min-Heap" in mode:
            due = datetime.now() + timedelta(minutes=10)
            ok, msg, tx = self.engine.queue_priority_transaction(
                TransactionType.TRANSFER, src, dst, amt, due_time=due, description="Priority Scheduled Transfer"
            )
        else:
            ok, msg, tx = self.engine.queue_regular_transaction(
                TransactionType.TRANSFER, src, dst, amt, description="Regular Batched Transfer"
            )

        if ok:
            messagebox.showinfo("Queued", msg)
            self.refresh_all()
            self.log_status(msg)
        else:
            messagebox.showerror("Failed", msg)
            self.log_status(msg, is_error=True)

    def _on_process_regular(self):
        ok, msg, tx = self.engine.process_next_regular()
        if ok:
            self.refresh_all()
            self.log_status(f"Processed Regular Tx: {msg}")
        else:
            messagebox.showwarning("Notice", msg)

    def _on_process_priority(self):
        ok, msg, tx = self.engine.process_next_priority()
        if ok:
            self.refresh_all()
            self.log_status(f"Processed Priority Tx: {msg}")
        else:
            messagebox.showwarning("Notice", msg)

    def _on_process_all(self):
        ok_count, fail_count, logs = self.engine.process_all_queued()
        self.refresh_all()
        summary = f"Processed {ok_count} queued transactions ({fail_count} failed)."
        messagebox.showinfo("Batch Complete", summary)
        self.log_status(summary)

    def _on_undo_transaction(self):
        ok, msg, tx = self.engine.undo_last_transaction()
        if ok:
            messagebox.showinfo("Rollback Complete", msg)
            self.refresh_all()
            self.log_status(f"Rollback Complete: {msg}")
        else:
            messagebox.showwarning("Cannot Undo", msg)
            self.log_status(msg, is_error=True)

    def _on_generate_mini_statement(self):
        acc = self.combo_stmt_acc.get().strip()
        if not acc:
            messagebox.showwarning("Notice", "Select an account to view mini-statement.")
            return

        records = self.engine.get_mini_statement(acc, limit=5)
        self.tree_history.delete(*self.tree_history.get_children())
        for tx in records:
            d = tx.to_dict()
            self.tree_history.insert(
                "",
                "end",
                values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["status"], d["timestamp"], d["description"])
            )
        self.log_status(f"Mini-statement for account {acc}: Displaying {len(records)} transactions (DLL backward traversal).")

    def _on_apply_sort(self):
        sort_by = self.combo_sort_by.get()
        order = self.combo_sort_order.get()
        reverse = ("Descending" in order)

        sorted_txs, comps = self.engine.sort_transactions(by=sort_by, algorithm="merge", reverse=reverse)
        self.tree_history.delete(*self.tree_history.get_children())
        for tx in sorted_txs:
            d = tx.to_dict()
            self.tree_history.insert(
                "",
                "end",
                values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["status"], d["timestamp"], d["description"])
            )
        self.lbl_sort_metrics.config(text=f"Merge Sort: {comps} comparisons across {len(sorted_txs)} transactions.")
        self.log_status(f"Sorted {len(sorted_txs)} records by {sort_by} using Merge Sort ({comps} comparisons).")

    def _on_query_avl_range(self):
        try:
            start_hrs = float(self.entry_avl_start_hr.get().strip())
            end_hrs = float(self.entry_avl_end_hr.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Hours must be numbers.")
            return

        now = datetime.now()
        t1 = now - timedelta(hours=start_hrs)
        t2 = now - timedelta(hours=end_hrs)
        t_start = min(t1, t2)
        t_end = max(t1, t2)

        matches = self.engine.query_date_range(t_start, t_end)

        self.tree_avl.delete(*self.tree_avl.get_children())
        for m in matches:
            d = m.to_dict()
            self.tree_avl.insert(
                "",
                "end",
                values=(d["tx_id"], d["timestamp"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}", d["status"])
            )

        tree_info = f"AVL Height: {self.engine.avl_index.get_height()} | Nodes: {self.engine.avl_index.total_nodes} | Matches: {len(matches)}"
        self.lbl_avl_tree_stats.config(text=tree_info)
        self.log_status(f"AVL Tree Query: Found {len(matches)} transactions in range [{t_start.strftime('%H:%M')} - {t_end.strftime('%H:%M')}].")

    def _on_run_bfs(self):
        start = self.combo_bfs_start.get().strip()
        if not start:
            messagebox.showwarning("Notice", "Select an account for BFS exploration.")
            return

        results = self.engine.get_connected_accounts_bfs(start)
        self.txt_graph_log.delete("1.0", tk.END)
        self.txt_graph_log.insert(tk.END, f"=== BREADTH-FIRST SEARCH (BFS) TRAVERSAL ===\n")
        self.txt_graph_log.insert(tk.END, f"Root Account: {start}\n")
        self.txt_graph_log.insert(tk.END, f"Total Connected/Reachable Accounts: {len(results)}\n\n")

        for r in results:
            self.txt_graph_log.insert(tk.END, f"Account: {r['account']} | Hops (Distance): {r['hops']} | Cumulative Outflow: ₹{r['total_transferred']:,.2f}\n")

        self.log_status(f"BFS completed for A/C {start}. {len(results)} accounts reachable.")

    def _on_run_dfs_cycles(self):
        cycles = self.engine.detect_fraud_cycles_dfs()
        self.txt_graph_log.delete("1.0", tk.END)
        self.txt_graph_log.insert(tk.END, f"=== DEPTH-FIRST SEARCH (DFS) CIRCULAR CYCLE DETECTION ===\n")
        self.txt_graph_log.insert(tk.END, f"Identified Circular Loops: {len(cycles)}\n\n")

        if cycles:
            for idx, c in enumerate(cycles, 1):
                path_str = " -> ".join(c)
                self.txt_graph_log.insert(tk.END, f"Cycle #{idx} (POTENTIAL FRAUD / CIRCULAR FUND ROUTING):\n  {path_str}\n\n")
            self.log_status(f"DFS Cycle Detection: {len(cycles)} circular transfer loops flagged!", is_error=True)
        else:
            self.txt_graph_log.insert(tk.END, "✓ No circular fund loops detected in the current network.\n")
            self.log_status("DFS Cycle Detection: No circular loops found.")

    # =========================================================================
    # REFRESH ALL VIEWS
    # =========================================================================
    def refresh_all(self):
        self.update_stat_cards()
        self.populate_dropdowns()
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

    def populate_dropdowns(self):
        acc_nums = sorted([a.account_number for a in self.engine.get_all_accounts()])
        self.inst_from_acc["values"] = acc_nums
        self.inst_to_acc["values"] = acc_nums
        self.q_from_acc["values"] = acc_nums
        self.q_to_acc["values"] = acc_nums
        self.combo_stmt_acc["values"] = acc_nums
        self.combo_bfs_start["values"] = acc_nums

        if acc_nums:
            if not self.inst_from_acc.get() or self.inst_from_acc.get() not in acc_nums:
                self.inst_from_acc.set(acc_nums[0])
            if not self.inst_to_acc.get() or self.inst_to_acc.get() not in acc_nums:
                self.inst_to_acc.set(acc_nums[1] if len(acc_nums) > 1 else acc_nums[0])
            if not self.q_from_acc.get() or self.q_from_acc.get() not in acc_nums:
                self.q_from_acc.set(acc_nums[0])
            if not self.q_to_acc.get() or self.q_to_acc.get() not in acc_nums:
                self.q_to_acc.set(acc_nums[1] if len(acc_nums) > 1 else acc_nums[0])
            if not self.combo_stmt_acc.get() or self.combo_stmt_acc.get() not in acc_nums:
                self.combo_stmt_acc.set(acc_nums[0])
            if not self.combo_bfs_start.get() or self.combo_bfs_start.get() not in acc_nums:
                self.combo_bfs_start.set(acc_nums[0])

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
        self.tree_reg_queue.delete(*self.tree_reg_queue.get_children())
        for tx in self.engine.regular_queue.to_list():
            d = tx.to_dict()
            self.tree_reg_queue.insert("", "end", values=(d["tx_id"], d["type"], d["from_account"], d["to_account"], f"₹{d['amount']:,.2f}"))

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
