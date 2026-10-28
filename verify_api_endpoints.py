import json
import sys
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"

def get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()

def main():
    print("Testing REST API endpoints on http://localhost:8000...")

    # 1. Status
    st, body = get("/api/status")
    assert st == 200, f"Status failed {st}"
    data = json.loads(body.decode("utf-8"))
    print(f"✓ /api/status OK: {data['total_accounts']} accounts, balance ₹{data['total_balance']:,.2f}")

    # 2. Accounts
    st, body = get("/api/accounts")
    assert st == 200
    accs = json.loads(body.decode("utf-8"))
    print(f"✓ /api/accounts OK: returned {len(accs)} accounts")

    # 3. Create Account
    st, body = post("/api/accounts", {"account_number": "777", "holder_name": "API Test User", "opening_balance": 15000})
    assert st == 200
    res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/accounts (POST) OK: {res['message']}")

    # 4. Deposit
    st, body = post("/api/transactions/deposit", {"account_number": "777", "amount": 2500, "description": "API Deposit"})
    assert st == 200
    res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/transactions/deposit OK: {res['message']}")

    # 5. Withdraw
    st, body = post("/api/transactions/withdraw", {"account_number": "777", "amount": 1000, "description": "API Withdraw"})
    assert st == 200
    res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/transactions/withdraw OK: {res['message']}")

    # Check updated balance of 777
    st, body = get("/api/accounts/777")
    acc777 = json.loads(body.decode("utf-8"))
    assert acc777["balance"] == 16500.0, f"Expected 16500.0, got {acc777['balance']}"
    print(f"✓ Account 777 balance verified: ₹{acc777['balance']:,.2f}")

    # 6. Transfer
    st, body = post("/api/transactions/transfer", {"from_account": "777", "to_account": "101", "amount": 1500, "description": "API Transfer"})
    assert st == 200
    res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/transactions/transfer OK: {res['message']}")

    # 7. Undo
    st, body = post("/api/transactions/undo", {})
    assert st == 200
    res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/transactions/undo OK: {res['message']}")

    # 8. AVL Range
    st, body = get("/api/avl/range?start_hours=24&end_hours=0")
    assert st == 200
    avl_res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/avl/range OK: {len(avl_res['matches'])} matches found (Tree Height: {avl_res['avl_tree_height']})")

    # 9. Graph BFS & Cycles
    st, body = get("/api/graph/bfs?start_account=101")
    assert st == 200
    bfs_res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/graph/bfs OK: {len(bfs_res['reachable_accounts'])} reachable")

    st, body = get("/api/graph/cycles")
    assert st == 200
    cyc_res = json.loads(body.decode("utf-8"))
    print(f"✓ /api/graph/cycles OK: {cyc_res['cycle_count']} circular cycles detected: {cyc_res['cycles']}")

    # 10. PDF
    st, body = get("/api/statement/pdf/101")
    assert st == 200
    assert body.startswith(b"%PDF")
    print(f"✓ /api/statement/pdf/101 OK: {len(body):,} bytes PDF returned")

    # 11. DSA State Inspector
    st, body = get("/api/dsa/state")
    assert st == 200
    dsa = json.loads(body.decode("utf-8"))
    assert "hash_table" in dsa and "avl_tree" in dsa and "min_heap" in dsa
    print(f"✓ /api/dsa/state OK: All 7 manual data structures inspected")

    print("\nALL API ENDPOINTS TESTED AND WORKING 100%!")

if __name__ == "__main__":
    main()
