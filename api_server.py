"""
FastAPI Server connecting the Next.js Frontend with the Python Data Structures & Algorithms Engine.
Provides complete RESTful API coverage for banking operations, PDF statement generation,
and live DSA state inspection.
"""
from datetime import datetime, timedelta
import io
import os
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.bank_engine import BankEngine
from core.models import Account, Transaction, TransactionType, TransactionStatus
from core.statement_pdf import generate_bank_statement_pdf
from performance.benchmarks import benchmark_searching, benchmark_sorting


app = FastAPI(
    title="BankFlow DSA Engine API",
    description="Backend API powering the modern Next.js Banking Platform and DSA Inspector",
    version="2.0.0"
)

# Enable CORS for Next.js development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Central singleton instance of BankEngine
engine = BankEngine()
engine.seed_demo_data()


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------
class CreateAccountRequest(BaseModel):
    account_number: str
    holder_name: str
    opening_balance: float = 0.0


class DepositWithdrawRequest(BaseModel):
    account_number: str
    amount: float
    description: Optional[str] = ""


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float
    description: Optional[str] = ""


class QueueTransactionRequest(BaseModel):
    type: str = "TRANSFER"  # DEPOSIT, WITHDRAWAL, TRANSFER
    from_account: str
    to_account: Optional[str] = None
    amount: float
    description: Optional[str] = ""
    is_priority: bool = False
    due_in_minutes: Optional[float] = 10.0


# -----------------------------------------------------------------------------
# 1. System Status & Summary Stats
# -----------------------------------------------------------------------------
@app.get("/api/status")
def get_system_status():
    accounts = engine.get_all_accounts()
    total_balance = engine.get_total_bank_balance()
    ht_stats = engine.accounts.bucket_collision_stats()

    return {
        "status": "online",
        "total_accounts": len(accounts),
        "total_balance": total_balance,
        "regular_queue_size": engine.regular_queue.size(),
        "priority_queue_size": engine.priority_queue.size(),
        "history_size": engine.history.size(),
        "undo_stack_size": engine.undo_stack.size(),
        "avl_tree_nodes": engine.avl_index.total_nodes,
        "avl_tree_height": engine.avl_index.get_height(),
        "graph_transfers_count": engine.transfer_graph.get_summary()["total_transfers"],
        "hash_table_stats": ht_stats
    }


@app.post("/api/reset-demo")
def reset_demo_data():
    engine.seed_demo_data()
    return {"message": "Demo data reset successfully."}


# -----------------------------------------------------------------------------
# 2. Account Management (Hash Table)
# -----------------------------------------------------------------------------
@app.get("/api/accounts")
def list_accounts():
    accounts = engine.get_all_accounts()
    return [acc.to_dict() for acc in sorted(accounts, key=lambda a: a.account_number)]


@app.post("/api/accounts")
def create_account(req: CreateAccountRequest):
    ok, msg = engine.create_account(
        account_number=req.account_number,
        holder_name=req.holder_name,
        opening_balance=req.opening_balance
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    acc = engine.get_account(req.account_number)
    return {"message": msg, "account": acc.to_dict() if acc else None}


@app.get("/api/accounts/{account_number}")
def get_account_detail(account_number: str):
    acc = engine.get_account(account_number)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc.to_dict()


@app.get("/api/accounts/{account_number}/lookup-comparison")
def compare_account_lookup(account_number: str):
    return engine.compare_account_lookup(account_number)


# -----------------------------------------------------------------------------
# 3. Direct Banking Transactions (Deposit, Withdraw, Transfer)
# -----------------------------------------------------------------------------
@app.post("/api/transactions/deposit")
def direct_deposit(req: DepositWithdrawRequest):
    ok, msg, tx = engine.execute_immediate(
        TransactionType.DEPOSIT,
        from_account=req.account_number,
        to_account=None,
        amount=req.amount,
        description=req.description or "Direct Deposit"
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "transaction": tx.to_dict() if tx else None}


@app.post("/api/transactions/withdraw")
def direct_withdraw(req: DepositWithdrawRequest):
    ok, msg, tx = engine.execute_immediate(
        TransactionType.WITHDRAWAL,
        from_account=req.account_number,
        to_account=None,
        amount=req.amount,
        description=req.description or "Direct Cash Withdrawal"
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "transaction": tx.to_dict() if tx else None}


@app.post("/api/transactions/transfer")
def direct_transfer(req: TransferRequest):
    ok, msg, tx = engine.execute_immediate(
        TransactionType.TRANSFER,
        from_account=req.from_account,
        to_account=req.to_account,
        amount=req.amount,
        description=req.description or "Direct Funds Transfer"
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "transaction": tx.to_dict() if tx else None}


# -----------------------------------------------------------------------------
# 4. Transaction Queuing & Processing (Circular Queue & Min-Heap)
# -----------------------------------------------------------------------------
@app.post("/api/transactions/queue")
def queue_transaction(req: QueueTransactionRequest):
    tx_type = TransactionType[req.type.upper()]
    if req.is_priority:
        due = datetime.now() + timedelta(minutes=req.due_in_minutes or 10.0)
        ok, msg, tx = engine.queue_priority_transaction(
            tx_type=tx_type,
            from_account=req.from_account,
            to_account=req.to_account,
            amount=req.amount,
            due_time=due,
            description=req.description or f"Scheduled Priority Payment (due {due.strftime('%H:%M')})"
        )
    else:
        ok, msg, tx = engine.queue_regular_transaction(
            tx_type=tx_type,
            from_account=req.from_account,
            to_account=req.to_account,
            amount=req.amount,
            description=req.description or "Regular Queued Transaction"
        )

    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "transaction": tx.to_dict() if tx else None}


@app.get("/api/transactions/queues")
def list_queues():
    reg_items = [tx.to_dict() for tx in engine.regular_queue.to_list()]
    pri_items = [tx.to_dict() for tx in engine.priority_queue.to_sorted_list()]
    return {
        "regular_queue": reg_items,
        "priority_queue": pri_items
    }


@app.post("/api/transactions/process-next-regular")
def process_next_regular():
    ok, msg, tx = engine.process_next_regular()
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "transaction": tx.to_dict() if tx else None}


@app.post("/api/transactions/process-next-priority")
def process_next_priority():
    ok, msg, tx = engine.process_next_priority()
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "transaction": tx.to_dict() if tx else None}


@app.post("/api/transactions/process-all")
def process_all_queued():
    ok_count, fail_count, logs = engine.process_all_queued()
    return {
        "processed_count": ok_count,
        "failed_count": fail_count,
        "logs": logs
    }


# -----------------------------------------------------------------------------
# 5. Undo / Rollback Engine (Stack)
# -----------------------------------------------------------------------------
@app.post("/api/transactions/undo")
def undo_transaction():
    ok, msg, tx = engine.undo_last_transaction()
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "undone_transaction": tx.to_dict() if tx else None}


# -----------------------------------------------------------------------------
# 6. History, Mini-Statements (DLL) & PDF Statement Generation
# -----------------------------------------------------------------------------
@app.get("/api/history")
def get_transaction_history(
    sort_by: Optional[str] = "date",
    algorithm: Optional[str] = "merge",
    reverse: Optional[bool] = True
):
    if sort_by in ["amount", "date"]:
        sorted_txs, comps = engine.sort_transactions(by=sort_by, algorithm=algorithm, reverse=reverse)
        return {
            "transactions": [tx.to_dict() for tx in sorted_txs],
            "algorithm": algorithm,
            "comparisons": comps
        }
    else:
        history = engine.get_all_history(newest_first=reverse)
        return {"transactions": [tx.to_dict() for tx in history], "algorithm": "none", "comparisons": 0}


@app.get("/api/statement/mini/{account_number}")
def get_mini_statement(account_number: str, limit: int = 5):
    records = engine.get_mini_statement(account_number, limit=limit)
    return [r.to_dict() for r in records]


@app.get("/api/statement/pdf/{account_number}")
def download_statement_pdf(
    account_number: str,
    start_days: Optional[int] = 30
):
    """
    Returns an official, downloadable bank statement PDF.
    """
    acc = engine.get_account(account_number)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # Get all transactions for this account from DLL
    all_txs = engine.get_all_history(newest_first=False)
    acc_txs = [tx for tx in all_txs if tx.from_account == account_number or tx.to_account == account_number]

    start_date = datetime.now() - timedelta(days=start_days)
    end_date = datetime.now()

    pdf_bytes = generate_bank_statement_pdf(
        account=acc,
        transactions=acc_txs,
        start_date=start_date,
        end_date=end_date
    )

    filename = f"Statement_AC_{account_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# -----------------------------------------------------------------------------
# 7. Date Range Queries (AVL Tree)
# -----------------------------------------------------------------------------
@app.get("/api/avl/range")
def query_avl_date_range(start_hours: float = 6.0, end_hours: float = 0.0):
    now = datetime.now()
    t_start = now - timedelta(hours=start_hours)
    t_end = now - timedelta(hours=end_hours)
    results = engine.query_date_range(t_start, t_end)
    return {
        "start_time": t_start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": t_end.strftime("%Y-%m-%d %H:%M:%S"),
        "matches": [tx.to_dict() for tx in results],
        "avl_tree_height": engine.avl_index.get_height(),
        "total_avl_nodes": engine.avl_index.total_nodes
    }


# -----------------------------------------------------------------------------
# 8. Graph Analysis: BFS & DFS Circular Cycle Detection
# -----------------------------------------------------------------------------
@app.get("/api/graph/bfs")
def get_graph_bfs(start_account: str):
    connected = engine.get_connected_accounts_bfs(start_account)
    return {
        "start_account": start_account,
        "reachable_accounts": connected
    }


@app.get("/api/graph/cycles")
def get_graph_cycles():
    cycles = engine.detect_fraud_cycles_dfs()
    return {
        "cycle_count": len(cycles),
        "cycles": cycles
    }


@app.get("/api/graph/edges")
def get_graph_edges():
    edges = []
    for from_acc, transfer_edges in engine.transfer_graph.adj_list.items():
        for e in transfer_edges:
            edges.append(e.to_dict())
    return edges


# -----------------------------------------------------------------------------
# 9. Performance Benchmarks
# -----------------------------------------------------------------------------
@app.get("/api/performance/benchmarks")
def run_performance_benchmarks(
    suite: str = "search",
    scale: str = "fast"
):
    if scale == "full":
        sizes = [1000, 5000, 10000, 25000, 50000, 100000]
    else:
        sizes = [1000, 5000, 10000, 20000]

    if suite == "search":
        results = benchmark_searching(sizes)
    else:
        sort_sizes = [s for s in sizes if s <= 25000]
        results = benchmark_sorting(sort_sizes)

    return results


# -----------------------------------------------------------------------------
# 10. Live DSA State Inspector (For "Behind-the-Scenes" Evaluator Console)
# -----------------------------------------------------------------------------
@app.get("/api/dsa/state")
def get_live_dsa_state():
    """
    Exposes complete internal structure of all 7 data structures
    for live visual inspection and interactive control.
    """
    # 1. Hash Table inspection
    ht = engine.accounts
    ht_buckets = []
    for idx, head in enumerate(ht.buckets):
        chain = []
        curr = head
        while curr:
            chain.append({"key": curr.key, "holder": curr.value.holder_name, "balance": curr.value.balance})
            curr = curr.next
        if chain:
            ht_buckets.append({"bucket_index": idx, "chain_length": len(chain), "nodes": chain})

    # 2. Circular Queue inspection
    cq = engine.regular_queue
    cq_slots = []
    for i in range(cq.capacity):
        item = cq.queue[i]
        cq_slots.append({
            "slot_index": i,
            "has_item": item is not None,
            "tx_id": item.tx_id if item else None,
            "is_front": i == cq.front and not cq.is_empty(),
            "is_rear": i == cq.rear
        })

    # 3. Min-Heap inspection
    heap = engine.priority_queue
    heap_nodes = []
    for idx, node in enumerate(heap.heap):
        heap_nodes.append({
            "index": idx,
            "key": node.key.strftime("%H:%M:%S") if isinstance(node.key, datetime) else str(node.key),
            "tx_id": node.value.tx_id,
            "amount": node.value.amount,
            "parent_index": (idx - 1) // 2 if idx > 0 else None
        })

    # 4. Doubly Linked List inspection
    dll = engine.history
    dll_nodes = []
    curr = dll.head
    idx = 0
    while curr and idx < 15:  # sample first 15
        dll_nodes.append({
            "index": idx,
            "tx_id": curr.data.tx_id,
            "amount": curr.data.amount,
            "has_prev": curr.prev is not None,
            "has_next": curr.next is not None
        })
        curr = curr.next
        idx += 1

    # 5. Stack inspection
    stack = engine.undo_stack
    stack_frames = []
    curr = stack.top
    idx = 0
    while curr and idx < 10:
        stack_frames.append({
            "level": idx,
            "tx_id": curr.data.tx_id,
            "type": curr.data.tx_type.value,
            "amount": curr.data.amount
        })
        curr = curr.next
        idx += 1

    # 6. Graph Summary
    graph_edges = []
    for from_acc, transfer_edges in engine.transfer_graph.adj_list.items():
        for e in transfer_edges:
            graph_edges.append(e.to_dict())

    return {
        "hash_table": {
            "capacity": ht.capacity,
            "count": ht.count,
            "load_factor": round(ht.load_factor(), 4),
            "max_load_factor": ht.MAX_LOAD_FACTOR,
            "resize_count": ht.resize_count,
            "active_buckets": ht_buckets
        },
        "circular_queue": {
            "capacity": cq.capacity,
            "count": cq.count,
            "front": cq.front,
            "rear": cq.rear,
            "slots": cq_slots[:16]  # show first 16 slots
        },
        "min_heap": {
            "size": heap.size(),
            "nodes": heap_nodes
        },
        "doubly_linked_list": {
            "size": dll.size(),
            "head_tx": dll.head.data.tx_id if dll.head else None,
            "tail_tx": dll.tail.data.tx_id if dll.tail else None,
            "sample_chain": dll_nodes
        },
        "undo_stack": {
            "depth": stack.size(),
            "top_tx": stack.peek().tx_id if stack.peek() else None,
            "frames": stack_frames
        },
        "avl_tree": {
            "total_nodes": engine.avl_index.total_nodes,
            "total_entries": engine.avl_index.total_entries,
            "height": engine.avl_index.get_height()
        },
        "graph": {
            "total_accounts": len(engine.transfer_graph.vertices),
            "total_transfers": len(graph_edges),
            "edges": graph_edges
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
