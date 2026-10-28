import { Account, Transaction, SystemStatus, LookupComparison, DSAState } from '../types/bank';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async getStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  async getAccounts(): Promise<Account[]> {
    const res = await fetch(`${API_BASE}/api/accounts`);
    if (!res.ok) throw new Error('Failed to fetch accounts');
    return res.json();
  },

  async createAccount(account_number: string, holder_name: string, opening_balance: number): Promise<{ message: string; account: Account }> {
    const res = await fetch(`${API_BASE}/api/accounts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_number, holder_name, opening_balance })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to create account');
    return data;
  },

  async getAccount(account_number: string): Promise<Account> {
    const res = await fetch(`${API_BASE}/api/accounts/${account_number}`);
    if (!res.ok) throw new Error('Account not found');
    return res.json();
  },

  async compareLookup(account_number: string): Promise<LookupComparison> {
    const res = await fetch(`${API_BASE}/api/accounts/${account_number}/lookup-comparison`);
    if (!res.ok) throw new Error('Failed to run lookup comparison');
    return res.json();
  },

  async deposit(account_number: string, amount: number, description?: string): Promise<{ message: string; transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/deposit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_number, amount, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Deposit failed');
    return data;
  },

  async withdraw(account_number: string, amount: number, description?: string): Promise<{ message: string; transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/withdraw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_number, amount, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Withdrawal failed');
    return data;
  },

  async transfer(from_account: string, to_account: string, amount: number, description?: string): Promise<{ message: string; transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/transfer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from_account, to_account, amount, description })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Transfer failed');
    return data;
  },

  async queueTransaction(
    type: 'DEPOSIT' | 'WITHDRAWAL' | 'TRANSFER',
    from_account: string,
    to_account?: string,
    amount: number = 0,
    is_priority: boolean = false,
    due_in_minutes: number = 10,
    description?: string
  ): Promise<{ message: string; transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/queue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type,
        from_account,
        to_account: to_account || null,
        amount,
        is_priority,
        due_in_minutes,
        description
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to queue transaction');
    return data;
  },

  async getQueues(): Promise<{ regular_queue: Transaction[]; priority_queue: Transaction[] }> {
    const res = await fetch(`${API_BASE}/api/transactions/queues`);
    if (!res.ok) throw new Error('Failed to fetch queues');
    return res.json();
  },

  async processNextRegular(): Promise<{ message: string; transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/process-next-regular`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to process regular transaction');
    return data;
  },

  async processNextPriority(): Promise<{ message: string; transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/process-next-priority`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to process priority transaction');
    return data;
  },

  async processAll(): Promise<{ processed_count: number; failed_count: number; logs: string[] }> {
    const res = await fetch(`${API_BASE}/api/transactions/process-all`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to process all transactions');
    return res.json();
  },

  async undoTransaction(): Promise<{ message: string; undone_transaction: Transaction }> {
    const res = await fetch(`${API_BASE}/api/transactions/undo`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Undo failed');
    return data;
  },

  async getHistory(sort_by = 'date', algorithm = 'merge', reverse = true): Promise<{ transactions: Transaction[]; algorithm: string; comparisons: number }> {
    const res = await fetch(`${API_BASE}/api/history?sort_by=${sort_by}&algorithm=${algorithm}&reverse=${reverse}`);
    if (!res.ok) throw new Error('Failed to fetch transaction history');
    return res.json();
  },

  async getMiniStatement(account_number: string, limit = 5): Promise<Transaction[]> {
    const res = await fetch(`${API_BASE}/api/statement/mini/${account_number}?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch mini statement');
    return res.json();
  },

  getPdfStatementUrl(account_number: string, start_days = 30): string {
    return `${API_BASE}/api/statement/pdf/${account_number}?start_days=${start_days}`;
  },

  async queryAvlRange(start_hours = 6.0, end_hours = 0.0): Promise<{
    start_time: string;
    end_time: string;
    matches: Transaction[];
    avl_tree_height: number;
    total_avl_nodes: number;
  }> {
    const res = await fetch(`${API_BASE}/api/avl/range?start_hours=${start_hours}&end_hours=${end_hours}`);
    if (!res.ok) throw new Error('Failed to query AVL tree');
    return res.json();
  },

  async getGraphBfs(start_account: string): Promise<{ start_account: string; reachable_accounts: Array<any> }> {
    const res = await fetch(`${API_BASE}/api/graph/bfs?start_account=${start_account}`);
    if (!res.ok) throw new Error('Failed to query graph BFS');
    return res.json();
  },

  async getGraphCycles(): Promise<{ cycle_count: number; cycles: Array<string[]> }> {
    const res = await fetch(`${API_BASE}/api/graph/cycles`);
    if (!res.ok) throw new Error('Failed to query graph cycles');
    return res.json();
  },

  async getPerformanceBenchmarks(suite = 'search', scale = 'fast'): Promise<any> {
    const res = await fetch(`${API_BASE}/api/performance/benchmarks?suite=${suite}&scale=${scale}`);
    if (!res.ok) throw new Error('Failed to run benchmarks');
    return res.json();
  },

  async getDSAState(): Promise<DSAState> {
    const res = await fetch(`${API_BASE}/api/dsa/state`);
    if (!res.ok) throw new Error('Failed to fetch DSA state');
    return res.json();
  },

  async resetDemo(): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/api/reset-demo`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset demo data');
    return res.json();
  }
};
