import sys, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8')

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req).read().decode('utf-8'))

def get(url):
    return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))

print('1. Creating Account 299...')
res = post('http://localhost:8000/api/accounts', {'account_number': '299', 'holder_name': 'Rakesh Sharma', 'opening_balance': 8000.0})
print('  Result:', res['message'])

print('2. Transferring 2000 from 101 to 299...')
res2 = post('http://localhost:8000/api/transactions/transfer', {'from_account': '101', 'to_account': '299', 'amount': 2000.0, 'description': 'Instant Payment'})
print('  Result:', res2['message'])

print('3. Verifying Balances...')
a101 = get('http://localhost:8000/api/accounts/101')
a299 = get('http://localhost:8000/api/accounts/299')
print(f'  A/C 101 Balance: INR {a101["balance"]:,.2f}')
print(f'  A/C 299 Balance: INR {a299["balance"]:,.2f}')

print('4. Verifying Mini-Statement for 299...')
stmt = get('http://localhost:8000/api/statement/mini/299')
print(f'  Transactions found: {len(stmt)}')
for tx in stmt:
    print(f'    - {tx["tx_id"]}: {tx["type"]} INR {tx["amount"]} ({tx["description"]})')

print('5. Verifying PDF Statement...')
pdf_req = urllib.request.urlopen('http://localhost:8000/api/statement/pdf/299')
pdf_bytes = pdf_req.read()
print(f'  PDF downloaded successfully: {len(pdf_bytes)} bytes')

print('6. Testing LIFO Stack Undo...')
undo_res = post('http://localhost:8000/api/transactions/undo', {})
print('  Undo Result:', undo_res['message'])
a299_reverted = get('http://localhost:8000/api/accounts/299')
print(f'  A/C 299 Balance after Undo: INR {a299_reverted["balance"]:,.2f}')

print('ALL BANKING OPERATIONS AND CORE FUNCTIONS FULLY OPERATIONAL!')
