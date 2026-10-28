'use client';

import React, { useState, useEffect } from 'react';
import {
  Building2,
  CreditCard,
  ArrowUpRight,
  ArrowDownLeft,
  ArrowLeftRight,
  Clock,
  ShieldCheck,
  FileText,
  Download,
  RotateCcw,
  Search,
  PlusCircle,
  TrendingUp,
  AlertTriangle,
  Layers,
  Cpu,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
  Network,
  Calendar,
  Sparkles,
  Zap,
  ExternalLink,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { Account, Transaction, SystemStatus, DSAState } from '../types/bank';

export default function BankingApp() {
  // Navigation & View state
  const [activeTab, setActiveTab] = useState<'overview' | 'accounts' | 'transfers' | 'statements' | 'security'>('overview');
  const [dsaConsoleOpen, setDsaConsoleOpen] = useState(false);
  const [dsaActiveTab, setDsaActiveTab] = useState<'hashtable' | 'queue' | 'heap' | 'dll' | 'stack' | 'avl' | 'graph'>('hashtable');

  // Core Data State
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [history, setHistory] = useState<Transaction[]>([]);
  const [queues, setQueues] = useState<{ regular_queue: Transaction[]; priority_queue: Transaction[] }>({ regular_queue: [], priority_queue: [] });
  const [dsaState, setDsaState] = useState<DSAState | null>(null);
  const [loading, setLoading] = useState(true);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error' | 'info'; text: string; action?: { label: string; onClick: () => void } } | null>(null);

  // Form states: Default to instant settlement so transfers reflect immediately on ledger
  const [transferType, setTransferType] = useState<'instant' | 'standard' | 'priority'>('instant');
  const [fromAcc, setFromAcc] = useState('');
  const [toAcc, setToAcc] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [dueMins, setDueMins] = useState('10');

  // Account creation form
  const [newAccNum, setNewAccNum] = useState('');
  const [newAccName, setNewAccName] = useState('');
  const [newAccBal, setNewAccBal] = useState('5000');

  // Deposit & Withdraw Modal states
  const [depositModalOpen, setDepositModalOpen] = useState(false);
  const [depositAmount, setDepositAmount] = useState('5000');
  const [withdrawModalOpen, setWithdrawModalOpen] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('2000');

  // Statement Filters
  const [stmtAccount, setStmtAccount] = useState('');
  const [stmtDays, setStmtDays] = useState(30);

  // Security / Graph state
  const [bfsAccount, setBfsAccount] = useState('101');
  const [bfsResults, setBfsResults] = useState<any[]>([]);
  const [fraudCycles, setFraudCycles] = useState<string[][]>([]);

  // Search state (Direct Hash Table lookup O(1))
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResult, setSearchResult] = useState<Account | null>(null);
  const [searchNotFound, setSearchNotFound] = useState(false);

  // AVL Date range state
  const [avlStartHours, setAvlStartHours] = useState('6');
  const [avlEndHours, setAvlEndHours] = useState('0');
  const [avlMatches, setAvlMatches] = useState<Transaction[]>([]);

  // UI helpers
  const [hideBalance, setHideBalance] = useState(false);

  // Initial Data Fetch
  const loadData = async () => {
    try {
      setLoading(true);
      const [statusData, accsData, histData, queuesData, dsaData] = await Promise.all([
        api.getStatus(),
        api.getAccounts(),
        api.getHistory('date', 'merge', true),
        api.getQueues(),
        api.getDSAState()
      ]);

      setStatus(statusData);
      setAccounts(accsData);
      setHistory(histData.transactions);
      setQueues(queuesData);
      setDsaState(dsaData);

      if (accsData.length > 0) {
        setSelectedAccount((prev) => {
          if (!prev) return accsData[0];
          const matched = accsData.find((a) => a.account_number === prev.account_number);
          return matched || accsData[0];
        });
        setFromAcc((prev) => prev || accsData[0].account_number);
        setStmtAccount((prev) => prev || accsData[0].account_number);
      }
    } catch (err: any) {
      console.error('Data load error:', err);
      showFeedback('error', 'Unable to connect to BankFlow backend. Please ensure python api_server.py is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const showFeedback = (type: 'success' | 'error' | 'info', text: string, action?: { label: string; onClick: () => void }) => {
    setFeedbackMsg({ type, text, action });
    setTimeout(() => setFeedbackMsg(null), 8000);
  };

  // ---------------------------------------------------------------------------
  // Action Handlers
  // ---------------------------------------------------------------------------
  const handleExecuteTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(amount);
    if (isNaN(val) || val <= 0) {
      showFeedback('error', 'Please enter a valid amount greater than 0.');
      return;
    }
    if (!toAcc.trim()) {
      showFeedback('error', 'Please enter or select a destination account.');
      return;
    }
    if (fromAcc === toAcc.trim()) {
      showFeedback('error', 'Source and destination accounts cannot be the same.');
      return;
    }

    try {
      if (transferType === 'instant') {
        const res = await api.transfer(fromAcc, toAcc.trim(), val, description || 'Instant Transfer');
        showFeedback('success', res.message);
      } else if (transferType === 'priority') {
        const mins = parseFloat(dueMins) || 10;
        const res = await api.queueTransaction('TRANSFER', fromAcc, toAcc.trim(), val, true, mins, description || `Priority Wire (Due in ${mins}m)`);
        showFeedback('info', `${res.message} Scheduled in Min-Heap.`, {
          label: '⚡ Process Now',
          onClick: handleProcessPriority
        });
      } else {
        const res = await api.queueTransaction('TRANSFER', fromAcc, toAcc.trim(), val, false, 0, description || 'Standard Batched Transfer');
        showFeedback('info', `${res.message} Queued in Circular Buffer.`, {
          label: '⚡ Clear Queue Now',
          onClick: handleProcessRegular
        });
      }
      setAmount('');
      setDescription('');
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message || 'Transaction could not be completed.');
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    const bal = parseFloat(newAccBal) || 0;
    try {
      const res = await api.createAccount(newAccNum, newAccName, bal);
      showFeedback('success', `${res.message}`);
      const createdAccNum = newAccNum;
      setNewAccNum('');
      setNewAccName('');
      setNewAccBal('5000');

      // Refresh data and select newly created account immediately
      const [statusData, accsData, histData, queuesData, dsaData] = await Promise.all([
        api.getStatus(),
        api.getAccounts(),
        api.getHistory('date', 'merge', true),
        api.getQueues(),
        api.getDSAState()
      ]);
      setStatus(statusData);
      setAccounts(accsData);
      setHistory(histData.transactions);
      setQueues(queuesData);
      setDsaState(dsaData);

      const createdAcc = accsData.find((a) => a.account_number === createdAccNum);
      if (createdAcc) {
        setSelectedAccount(createdAcc);
        setFromAcc(createdAcc.account_number);
        setStmtAccount(createdAcc.account_number);
      }
    } catch (err: any) {
      showFeedback('error', err.message || 'Failed to create account.');
    }
  };

  const handleDepositSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccount) return;
    const amt = parseFloat(depositAmount);
    if (isNaN(amt) || amt <= 0) {
      showFeedback('error', 'Please enter a valid deposit amount.');
      return;
    }
    try {
      const res = await api.deposit(selectedAccount.account_number, amt, 'Direct Branch Deposit');
      showFeedback('success', res.message);
      setDepositModalOpen(false);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message || 'Deposit failed.');
    }
  };

  const handleWithdrawSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccount) return;
    const amt = parseFloat(withdrawAmount);
    if (isNaN(amt) || amt <= 0) {
      showFeedback('error', 'Please enter a valid withdrawal amount.');
      return;
    }
    try {
      const res = await api.withdraw(selectedAccount.account_number, amt, 'ATM Cash Withdrawal');
      showFeedback('success', res.message);
      setWithdrawModalOpen(false);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message || 'Withdrawal failed.');
    }
  };

  const handleUndoTransaction = async () => {
    try {
      const res = await api.undoTransaction();
      showFeedback('success', `Rollback Complete: ${res.message}`);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message || 'Undo could not be completed.');
    }
  };

  const handleProcessRegular = async () => {
    try {
      const res = await api.processNextRegular();
      showFeedback('success', `Circular FIFO Clearing: ${res.message}`);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
    }
  };

  const handleProcessPriority = async () => {
    try {
      const res = await api.processNextPriority();
      showFeedback('success', `Min-Heap Earliest Priority: ${res.message}`);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
    }
  };

  const handleProcessAll = async () => {
    try {
      const res = await api.processAll();
      showFeedback('success', `Batch Complete: ${res.processed_count} cleared, ${res.failed_count} failed.`);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
    }
  };

  const handleResetDemo = async () => {
    if (confirm('Reset all demo accounts and transactions back to clean seed data?')) {
      try {
        const res = await api.resetDemo();
        showFeedback('info', res.message);
        await loadData();
      } catch (err: any) {
        showFeedback('error', err.message);
      }
    }
  };

  const handleRunSearchLookup = async () => {
    const q = searchQuery.trim();
    if (!q) {
      setSearchResult(null);
      setSearchNotFound(false);
      return;
    }
    try {
      const acc = await api.getAccount(q);
      setSearchResult(acc);
      setSearchNotFound(false);
    } catch (err: any) {
      setSearchResult(null);
      setSearchNotFound(true);
    }
  };

  const handleRunBfs = async () => {
    try {
      const res = await api.getGraphBfs(bfsAccount);
      setBfsResults(res.reachable_accounts);
    } catch (err: any) {
      showFeedback('error', 'BFS traversal failed.');
    }
  };

  const handleRunDfsCycles = async () => {
    try {
      const res = await api.getGraphCycles();
      setFraudCycles(res.cycles);
      if (res.cycles.length > 0) {
        showFeedback('error', `Security Alert: ${res.cycles.length} circular layering loop(s) detected via DFS!`);
      } else {
        showFeedback('success', 'Zero circular transfer loops detected in transfer network.');
      }
    } catch (err: any) {
      showFeedback('error', 'Cycle detection failed.');
    }
  };

  const handleRunAvlRange = async () => {
    try {
      const startH = parseFloat(avlStartHours) || 6.0;
      const endH = parseFloat(avlEndHours) || 0.0;
      const res = await api.queryAvlRange(startH, endH);
      setAvlMatches(res.matches);
      showFeedback('info', `AVL Tree Range Query returned ${res.matches.length} matches in O(log N + K) time.`);
    } catch (err: any) {
      showFeedback('error', 'AVL Range query failed.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* ===================================================================== */}
      {/* INSTITUTIONAL HEADER & NAVIGATION */}
      {/* ===================================================================== */}
      <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-600/30">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-extrabold tracking-tight text-base text-white flex items-center space-x-1.5">
                <span>NovaTrust</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono border border-cyan-800 uppercase">
                  BankFlow Core
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Automated Data Structures & Algorithms Engine</p>
            </div>
          </div>

          {/* Primary View Navigation */}
          <nav className="hidden md:flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-medium">
            {[
              { id: 'overview', label: 'Dashboard', icon: TrendingUp },
              { id: 'accounts', label: 'Accounts (Hash Table)', icon: Building2 },
              { id: 'transfers', label: 'Transfers & Clearing', icon: ArrowLeftRight },
              { id: 'statements', label: 'Official Statements', icon: FileText },
              { id: 'security', label: 'Anti-Fraud (Graph)', icon: ShieldCheck }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Header: DSA Toggle & Reset */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setDsaConsoleOpen(!dsaConsoleOpen)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition cursor-pointer ${
                dsaConsoleOpen
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50 shadow-md shadow-cyan-500/20'
                  : 'bg-slate-900 text-slate-300 border-slate-700 hover:border-slate-500'
              }`}
            >
              <Cpu className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              <span className="hidden sm:inline">⚡ DSA Engine Inspector</span>
              <span className="sm:hidden">DSA</span>
            </button>

            <button
              onClick={handleResetDemo}
              title="Reset Demo Dataset"
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 border border-transparent hover:border-slate-700 transition cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Mobile Navigation bar */}
        <div className="md:hidden flex overflow-x-auto px-4 py-2 border-t border-slate-800/80 bg-slate-950/70 text-xs gap-2">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'accounts', label: 'Accounts' },
            { id: 'transfers', label: 'Transfers' },
            { id: 'statements', label: 'Statements' },
            { id: 'security', label: 'Security' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1 rounded-md whitespace-nowrap ${
                activeTab === tab.id ? 'bg-cyan-600 text-white font-bold' : 'text-slate-400'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Global Feedback Banner */}
      {feedbackMsg && (
        <div
          className={`sticky top-16 z-30 px-4 py-2.5 text-xs font-medium flex items-center justify-between border-b shadow-lg transition-all ${
            feedbackMsg.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-300 border-emerald-800'
              : feedbackMsg.type === 'error'
              ? 'bg-rose-950/90 text-rose-300 border-rose-800'
              : 'bg-cyan-950/90 text-cyan-300 border-cyan-800'
          }`}
        >
          <div className="flex items-center space-x-2 max-w-4xl mx-auto w-full">
            {feedbackMsg.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
            {feedbackMsg.type === 'error' && <XCircle className="w-4 h-4 text-rose-400 shrink-0" />}
            {feedbackMsg.type === 'info' && <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />}
            <span className="flex-1">{feedbackMsg.text}</span>
            {feedbackMsg.action && (
              <button
                onClick={() => {
                  feedbackMsg.action?.onClick();
                  setFeedbackMsg(null);
                }}
                className="px-2.5 py-1 bg-white text-slate-900 rounded font-bold hover:bg-slate-200 transition text-[11px] cursor-pointer"
              >
                {feedbackMsg.action.label}
              </button>
            )}
            <button onClick={() => setFeedbackMsg(null)} className="opacity-75 hover:opacity-100 ml-2 cursor-pointer">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* DSA ENGINE LIVE INSPECTOR (THE 7 OPTIMAL CORE DATA STRUCTURES) */}
      {/* ===================================================================== */}
      {dsaConsoleOpen && (
        <section className="bg-slate-900 border-b border-cyan-500/30 p-4 transition-all animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="max-w-7xl mx-auto space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-800 pb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
                  <h2 className="text-sm font-bold tracking-tight text-white uppercase">
                    ⚡ Live DSA Engine Inspector (First Principles)
                  </h2>
                </div>
                <p className="text-xs text-slate-400">
                  Each banking feature is powered by its single optimal data structure and algorithm.
                </p>
              </div>

              {/* Status indicators */}
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span>
                  Load Factor: <strong className="text-cyan-300 font-mono">{dsaState?.hash_table.load_factor ?? 0}</strong> / 0.75
                </span>
                <span>
                  AVL Height: <strong className="text-emerald-300 font-mono">{dsaState?.avl_tree.height ?? 0}</strong>
                </span>
              </div>
            </div>

            {/* DSA Tabs (7 Distinct Component Structures) */}
            <div className="bg-slate-950 rounded-xl border border-slate-800 p-2">
              <div className="flex border-b border-slate-800 text-xs overflow-x-auto pb-1 gap-1">
                {[
                  { id: 'hashtable', label: '1. Hash Table (Accounts - O(1))', badge: `${dsaState?.hash_table.count} keys` },
                  { id: 'queue', label: '2. Circular Queue (FIFO - O(1))', badge: `${dsaState?.circular_queue.count} queued` },
                  { id: 'heap', label: '3. Min-Heap (Priority - O(log N))', badge: `${dsaState?.min_heap.size} wires` },
                  { id: 'dll', label: '4. Doubly Linked List (Ledger)', badge: `${dsaState?.doubly_linked_list.size} txs` },
                  { id: 'stack', label: '5. LIFO Stack (Undo - O(1))', badge: `${dsaState?.undo_stack.depth} ops` },
                  { id: 'avl', label: '6. AVL Tree (Timestamps)', badge: `h=${dsaState?.avl_tree.height}` },
                  { id: 'graph', label: '7. Graph (DFS Cycles & BFS)', badge: `${dsaState?.graph.total_transfers} transfers` }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setDsaActiveTab(tab.id as any)}
                    className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition flex items-center space-x-1.5 cursor-pointer ${
                      dsaActiveTab === tab.id
                        ? 'bg-cyan-600 text-white font-bold shadow'
                        : 'text-slate-400 hover:text-white hover:bg-slate-900'
                    }`}
                  >
                    <span>{tab.label}</span>
                    <span className="text-[10px] bg-slate-900/80 px-1.5 py-0.2 rounded font-mono text-cyan-300">
                      {tab.badge}
                    </span>
                  </button>
                ))}
              </div>

              {/* Tab 1: Hash Table */}
              {dsaActiveTab === 'hashtable' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px] uppercase">Capacity</div>
                      <div className="text-base font-bold font-mono text-white">{dsaState?.hash_table.capacity}</div>
                    </div>
                    <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px] uppercase">Total Keys</div>
                      <div className="text-base font-bold font-mono text-cyan-400">{dsaState?.hash_table.count}</div>
                    </div>
                    <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px] uppercase">Load Factor (λ)</div>
                      <div className="text-base font-bold font-mono text-emerald-400">{dsaState?.hash_table.load_factor}</div>
                    </div>
                    <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px] uppercase">Resize Triggers</div>
                      <div className="text-base font-bold font-mono text-purple-400">{dsaState?.hash_table.resize_count}</div>
                    </div>
                  </div>

                  <div className="text-slate-300 font-semibold text-[11px]">Separate Chaining Active Buckets:</div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 max-h-48 overflow-y-auto">
                    {dsaState?.hash_table.active_buckets.map((b) => (
                      <div key={b.bucket_index} className="bg-slate-900 p-2 rounded border border-slate-800">
                        <div className="font-mono text-cyan-400 font-bold">Bucket [{b.bucket_index}] (chain: {b.chain_length})</div>
                        <div className="mt-1 space-y-1">
                          {b.nodes.map((n) => (
                            <div key={n.key} className="text-[11px] text-slate-300 bg-slate-950 p-1 rounded font-mono">
                              A/C {n.key}: ₹{n.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 2: Circular Queue */}
              {dsaActiveTab === 'queue' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">
                      Circular Buffer Slots (Capacity: {dsaState?.circular_queue.capacity}, FRONT={dsaState?.circular_queue.front}, REAR={dsaState?.circular_queue.rear})
                    </span>
                    <div className="flex gap-2">
                      <button onClick={handleProcessRegular} className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold cursor-pointer">
                        Dequeue & Process Next (FIFO)
                      </button>
                      <button onClick={handleProcessAll} className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold cursor-pointer">
                        Clear All Queued
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
                    {dsaState?.circular_queue.slots.map((s) => (
                      <div
                        key={s.slot_index}
                        className={`p-2 rounded border text-center font-mono text-[11px] ${
                          s.is_front
                            ? 'bg-cyan-950 border-cyan-500 text-cyan-300 ring-1 ring-cyan-400'
                            : s.is_rear
                            ? 'bg-purple-950 border-purple-500 text-purple-300'
                            : s.has_item
                            ? 'bg-slate-800 border-slate-700 text-white'
                            : 'bg-slate-950 border-slate-800 text-slate-600'
                        }`}
                      >
                        <div>Slot {s.slot_index}</div>
                        <div className="font-bold truncate mt-0.5">{s.tx_id || '—'}</div>
                        {s.is_front && <div className="text-[9px] text-cyan-400 uppercase font-bold">FRONT</div>}
                        {s.is_rear && <div className="text-[9px] text-purple-400 uppercase font-bold">REAR</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: Min-Heap */}
              {dsaActiveTab === 'heap' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">Binary Min-Heap Priority Queue (Ordered by Scheduled Due Time)</span>
                    <button onClick={handleProcessPriority} className="px-3 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-semibold cursor-pointer">
                      Extract Min (Earliest Due)
                    </button>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {dsaState?.min_heap.nodes.map((n) => (
                      <div key={n.index} className="bg-slate-900 p-2.5 rounded border border-amber-900/60">
                        <div className="flex justify-between text-amber-400 font-bold font-mono">
                          <span>Node [{n.index}]</span>
                          <span>Due: {n.key}</span>
                        </div>
                        <div className="text-white font-mono mt-1">{n.tx_id}: ₹{n.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                        {n.parent_index !== null && (
                          <div className="text-[10px] text-slate-400 mt-1">Parent: Node [{n.parent_index}]</div>
                        )}
                      </div>
                    ))}
                    {dsaState?.min_heap.nodes.length === 0 && (
                      <div className="text-slate-500 italic py-2">Priority min-heap is currently empty.</div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 4: Doubly Linked List */}
              {dsaActiveTab === 'dll' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="text-slate-300">
                    Bidirectional Audit Chain (Total Nodes: {dsaState?.doubly_linked_list.size}, Head: {dsaState?.doubly_linked_list.head_tx}, Tail: {dsaState?.doubly_linked_list.tail_tx})
                  </div>
                  <div className="flex items-center gap-2 overflow-x-auto py-2">
                    {dsaState?.doubly_linked_list.sample_chain.map((node, i) => (
                      <React.Fragment key={node.tx_id}>
                        <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-700 min-w-[130px] font-mono text-center">
                          <div className="text-cyan-400 font-bold">{node.tx_id}</div>
                          <div className="text-[11px] text-emerald-400">₹{node.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                          <div className="text-[9px] text-slate-500 mt-1">
                            {node.has_prev ? '◀ PREV' : 'HEAD'} | {node.has_next ? 'NEXT ▶' : 'TAIL'}
                          </div>
                        </div>
                        {i < (dsaState?.doubly_linked_list.sample_chain.length || 0) - 1 && (
                          <span className="text-slate-600 font-bold">⇄</span>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 5: Undo Stack */}
              {dsaActiveTab === 'stack' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300">LIFO Undo Stack (Depth: {dsaState?.undo_stack.depth})</span>
                    <button onClick={handleUndoTransaction} className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold cursor-pointer">
                      Pop & Rollback Most Recent Op
                    </button>
                  </div>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto">
                    {dsaState?.undo_stack.frames.map((frame, i) => (
                      <div
                        key={frame.tx_id + i}
                        className={`p-2 rounded font-mono flex justify-between items-center ${
                          i === 0 ? 'bg-rose-950/60 border border-rose-700 text-rose-200' : 'bg-slate-900 border border-slate-800 text-slate-300'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] px-1 bg-slate-800 rounded font-bold">L{frame.level}</span>
                          <span>{frame.tx_id} ({frame.type})</span>
                        </div>
                        <span className="font-bold">₹{frame.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                      </div>
                    ))}
                    {dsaState?.undo_stack.frames.length === 0 && (
                      <div className="text-slate-500 italic py-2">Undo stack is currently empty.</div>
                    )}
                  </div>
                </div>
              )}

              {/* Tab 6: AVL Tree */}
              {dsaActiveTab === 'avl' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <span className="text-slate-300">
                        Self-Balancing AVL Search Tree (Height: {dsaState?.avl_tree.height}, Total Nodes: {dsaState?.avl_tree.total_nodes})
                      </span>
                      <p className="text-[11px] text-slate-400">Guarantees |hL - hR| ≤ 1 for O(log N + K) chronological queries</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        placeholder="Start hrs ago"
                        value={avlStartHours}
                        onChange={(e) => setAvlStartHours(e.target.value)}
                        className="w-20 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white"
                      />
                      <span className="text-slate-500">to</span>
                      <input
                        type="number"
                        placeholder="End hrs ago"
                        value={avlEndHours}
                        onChange={(e) => setAvlEndHours(e.target.value)}
                        className="w-20 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white"
                      />
                      <button onClick={handleRunAvlRange} className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold cursor-pointer">
                        Query Range
                      </button>
                    </div>
                  </div>

                  {avlMatches.length > 0 && (
                    <div className="bg-slate-900 p-2.5 rounded border border-slate-800 max-h-36 overflow-y-auto space-y-1 font-mono text-[11px]">
                      {avlMatches.map((m) => (
                        <div key={m.tx_id} className="flex justify-between text-slate-300">
                          <span>{m.timestamp} - {m.tx_id} ({m.type})</span>
                          <span className="text-emerald-400 font-bold">₹{m.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 7: Graph */}
              {dsaActiveTab === 'graph' && (
                <div className="p-3 text-xs space-y-3">
                  <div className="flex flex-wrap justify-between items-center gap-2">
                    <span className="text-slate-300">
                      Directed Transaction Graph (Vertices: {dsaState?.graph.total_accounts}, Directed Edges: {dsaState?.graph.total_transfers})
                    </span>
                    <button onClick={handleRunDfsCycles} className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold cursor-pointer">
                      Run DFS Cycle Detection
                    </button>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                    {dsaState?.graph.edges.map((e, idx) => (
                      <div key={idx} className="bg-slate-900 p-2 rounded border border-slate-800 font-mono text-[11px] flex justify-between items-center">
                        <span className="text-cyan-400">{e.from} ➔ {e.to}</span>
                        <span className="text-emerald-400 font-bold">₹{e.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ===================================================================== */}
      {/* MAIN BANKING WORKSPACE */}
      {/* ===================================================================== */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {/* VIEW 1: OVERVIEW & DASHBOARD */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Top Wealth & Account Overview Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Primary Balance Card */}
              <div className="lg:col-span-2 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Total Bank Portfolio Balance</span>
                    <div className="flex items-center space-x-3 mt-1.5">
                      <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                        {hideBalance ? '••••••••' : `₹${(status?.total_balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
                      </h1>
                      <button onClick={() => setHideBalance(!hideBalance)} className="text-slate-400 hover:text-slate-200 cursor-pointer">
                        {hideBalance ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                      </button>
                    </div>
                    <div className="flex items-center space-x-2 mt-2 text-xs text-emerald-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                      <span>Verified across {accounts.length} Institutional Accounts in Hash Table</span>
                    </div>
                  </div>

                  {/* Active Selected Account Card Badge */}
                  <div className="bg-gradient-to-tr from-cyan-600 to-blue-600 text-white p-3.5 rounded-xl shadow-lg shadow-cyan-600/20 text-right hidden sm:block">
                    <div className="text-[10px] tracking-wider uppercase opacity-80">Active Account</div>
                    <div className="text-base font-bold font-mono">A/C {selectedAccount?.account_number}</div>
                    <div className="text-xs opacity-90">{selectedAccount?.holder_name}</div>
                    <div className="text-[11px] font-mono mt-1 font-bold text-cyan-200">
                      ₹{selectedAccount?.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                </div>

                {/* Quick Action Ribbon */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-slate-800/80">
                  <button
                    onClick={() => {
                      if (selectedAccount) setFromAcc(selectedAccount.account_number);
                      setActiveTab('transfers');
                    }}
                    className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/80 border border-slate-700 text-left transition group cursor-pointer"
                  >
                    <ArrowUpRight className="w-5 h-5 text-cyan-400 mb-1 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
                    <div className="text-xs font-semibold text-white">Send Money</div>
                    <div className="text-[11px] text-slate-400">Instant Transfer</div>
                  </button>

                  <button
                    onClick={() => setDepositModalOpen(true)}
                    className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/80 border border-slate-700 text-left transition group cursor-pointer"
                  >
                    <ArrowDownLeft className="w-5 h-5 text-emerald-400 mb-1 group-hover:translate-y-0.5 transition" />
                    <div className="text-xs font-semibold text-white">Deposit Funds</div>
                    <div className="text-[11px] text-slate-400">Direct Credit</div>
                  </button>

                  <button
                    onClick={() => setWithdrawModalOpen(true)}
                    className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/80 border border-slate-700 text-left transition group cursor-pointer"
                  >
                    <CreditCard className="w-5 h-5 text-amber-400 mb-1" />
                    <div className="text-xs font-semibold text-white">Cash Withdrawal</div>
                    <div className="text-[11px] text-slate-400">Branch / ATM</div>
                  </button>

                  <button
                    onClick={() => {
                      if (selectedAccount) {
                        window.open(api.getPdfStatementUrl(selectedAccount.account_number, 30), '_blank');
                      }
                    }}
                    className="p-3 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800 text-left transition group cursor-pointer"
                  >
                    <Download className="w-5 h-5 text-cyan-400 mb-1" />
                    <div className="text-xs font-semibold text-white">Download PDF</div>
                    <div className="text-[11px] text-cyan-300/80">Official Statement</div>
                  </button>
                </div>
              </div>

              {/* Digital Platinum Card Widget */}
              <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6 rounded-2xl border border-indigo-900/60 shadow-xl flex flex-col justify-between text-white relative overflow-hidden">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[11px] font-semibold tracking-widest text-cyan-300">NOVATRUST PLATINUM</span>
                    <div className="text-xs text-slate-400">Commercial Business Card</div>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center font-bold text-xs text-cyan-300">
                    ◈
                  </div>
                </div>

                <div className="my-6">
                  <div className="text-lg font-mono tracking-widest text-slate-200">
                    4532 •••• •••• {selectedAccount?.account_number.slice(-4) || '8821'}
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>CARDHOLDER: {selectedAccount?.holder_name.toUpperCase()}</span>
                    <span>EXP: 09/31</span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs pt-3 border-t border-indigo-900/50">
                  <span className="text-emerald-400 font-medium">● ACTIVE IN HASH TABLE</span>
                  <span className="text-slate-400 font-mono">
                    ₹{selectedAccount?.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>

            {/* Middle Section: Recent Transactions & Active Accounts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Activity Table */}
              <div className="lg:col-span-2 bg-slate-900 rounded-2xl border border-slate-800 p-6">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h2 className="text-base font-bold text-white">Recent Ledger Transactions</h2>
                    <p className="text-xs text-slate-400">Sorted chronologically using Merge Sort</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('statements')}
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center space-x-1 cursor-pointer"
                  >
                    <span>View All</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="pb-3">Reference</th>
                        <th className="pb-3">Type</th>
                        <th className="pb-3">Account Flow</th>
                        <th className="pb-3">Amount</th>
                        <th className="pb-3">Date</th>
                        <th className="pb-3 text-right">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {history.slice(0, 8).map((tx) => (
                        <tr key={tx.tx_id} className="hover:bg-slate-800/30 transition">
                          <td className="py-3 font-mono font-medium text-cyan-400">{tx.tx_id}</td>
                          <td className="py-3 font-medium text-slate-200">{tx.type}</td>
                          <td className="py-3 text-slate-400 font-mono">
                            {tx.type === 'TRANSFER' ? `${tx.from_account} ➔ ${tx.to_account}` : `A/C ${tx.from_account}`}
                          </td>
                          <td className="py-3 font-mono font-bold text-white">
                            ₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </td>
                          <td className="py-3 text-slate-400">{tx.timestamp.split(' ')[0]}</td>
                          <td className="py-3 text-right">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                                tx.status === 'COMPLETED'
                                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                  : tx.status === 'FAILED'
                                  ? 'bg-rose-950 text-rose-400 border border-rose-800'
                                  : 'bg-amber-950 text-amber-400 border border-amber-800'
                              }`}
                            >
                              {tx.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {history.length === 0 && (
                        <tr>
                          <td colSpan={6} className="py-8 text-center text-slate-500">
                            No ledger transactions recorded yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Account Selector List & Dispute Undo */}
              <div className="space-y-6">
                <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                  <div className="flex justify-between items-center mb-1">
                    <h3 className="text-sm font-bold text-white">Your Accounts</h3>
                    <span className="text-[11px] text-cyan-400 font-mono">{accounts.length} active</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">Click to inspect or set active sender account</p>

                  <div className="space-y-2.5 max-h-60 overflow-y-auto">
                    {accounts.map((acc) => (
                      <div
                        key={acc.account_number}
                        onClick={() => {
                          setSelectedAccount(acc);
                          setFromAcc(acc.account_number);
                          setStmtAccount(acc.account_number);
                        }}
                        className={`p-3 rounded-xl border cursor-pointer transition ${
                          selectedAccount?.account_number === acc.account_number
                            ? 'bg-cyan-950/50 border-cyan-500 shadow-md ring-1 ring-cyan-500/40'
                            : 'bg-slate-800/40 border-slate-800 hover:bg-slate-800'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-semibold text-xs text-white">{acc.holder_name}</span>
                          <span className="font-mono text-xs font-bold text-emerald-400">
                            ₹{acc.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
                          <span>A/C: {acc.account_number}</span>
                          {selectedAccount?.account_number === acc.account_number && (
                            <span className="text-cyan-400 font-bold text-[10px]">● SELECTED</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Dispute / Transaction Reversal Card */}
                <div className="bg-gradient-to-br from-slate-900 to-rose-950/30 rounded-2xl border border-slate-800 p-5">
                  <div className="flex items-center space-x-2 text-rose-400 text-xs font-bold mb-1">
                    <RotateCcw className="w-4 h-4" />
                    <span>Transaction Reversal Center</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-3">
                    Dispute and safely roll back the most recent completed transaction using LIFO Stack.
                  </p>
                  <button
                    onClick={handleUndoTransaction}
                    className="w-full py-2 px-3 rounded-lg bg-rose-600/80 hover:bg-rose-600 text-white text-xs font-semibold transition cursor-pointer"
                  >
                    Request Last Transaction Reversal
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 2: COMMERCIAL ACCOUNTS */}
        {activeTab === 'accounts' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-white">Commercial Account Directory</h2>
                <p className="text-xs text-slate-400 mt-1">
                  High-performance account management powered by Separate-Chaining Hash Table O(1)
                </p>
              </div>

              {/* Direct Hash Table Search bar */}
              <div className="flex items-center space-x-2 w-full md:w-auto">
                <div className="relative flex-1 md:w-64">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search Account No..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRunSearchLookup()}
                  />
                </div>
                <button
                  onClick={handleRunSearchLookup}
                  className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium cursor-pointer"
                >
                  Lookup
                </button>
              </div>
            </div>

            {/* Direct Hash Table Lookup Result Display */}
            {searchResult && (
              <div className="bg-slate-900 border border-emerald-500/60 p-4 rounded-xl text-xs space-y-2">
                <div className="font-bold text-emerald-400 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-emerald-400" />
                    <span>Direct Hash Table Indexing O(1): Account Verified</span>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedAccount(searchResult);
                      setFromAcc(searchResult.account_number);
                      setActiveTab('transfers');
                    }}
                    className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold cursor-pointer"
                  >
                    Transfer with this Account ➔
                  </button>
                </div>
                <div className="text-slate-300">
                  Account <span className="font-mono font-bold text-white">#{searchResult.account_number}</span> (
                  {searchResult.holder_name}) was retrieved directly from the Hash Table bucket in O(1) time. Current Balance:{' '}
                  <span className="font-mono font-bold text-emerald-400">
                    ₹{searchResult.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            )}
            {searchNotFound && (
              <div className="bg-slate-900 border border-rose-800 p-3 rounded-xl text-xs text-rose-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                <span>Account "{searchQuery.trim()}" not found in Hash Table.</span>
              </div>
            )}

            {/* Accounts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {accounts.map((acc) => (
                <div
                  key={acc.account_number}
                  className={`bg-slate-900 border rounded-xl p-5 transition ${
                    selectedAccount?.account_number === acc.account_number
                      ? 'border-cyan-500 ring-1 ring-cyan-500/40'
                      : 'border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-white text-base">{acc.holder_name}</h3>
                      <p className="text-xs text-slate-400 font-mono">A/C: {acc.account_number}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
                      HASH O(1)
                    </span>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-end">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider">Available Balance</span>
                      <div className="text-xl font-bold font-mono text-emerald-400">
                        ₹{acc.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setSelectedAccount(acc);
                          setFromAcc(acc.account_number);
                          setActiveTab('transfers');
                        }}
                        className="px-2.5 py-1 rounded bg-cyan-950 hover:bg-cyan-900 text-xs text-cyan-300 font-medium cursor-pointer"
                      >
                        Transfer
                      </button>
                      <button
                        onClick={() => {
                          window.open(api.getPdfStatementUrl(acc.account_number, 30), '_blank');
                        }}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium flex items-center space-x-1 cursor-pointer"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>PDF</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Create Account Form */}
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 max-w-xl">
              <h3 className="text-base font-bold text-white mb-1 flex items-center gap-2">
                <PlusCircle className="w-5 h-5 text-cyan-400" /> Open New Commercial Account
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Creates account instantly in Hash Table and records initial opening balance deposit on ledger
              </p>

              <form onSubmit={handleCreateAccount} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Account Number (Digits only, min 3 digits):</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 109"
                    value={newAccNum}
                    onChange={(e) => setNewAccNum(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Customer Full Name / Business Title:</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Deepak Verma"
                    value={newAccName}
                    onChange={(e) => setNewAccName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Opening Deposit (INR ₹):</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    value={newAccBal}
                    onChange={(e) => setNewAccBal(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg transition cursor-pointer"
                >
                  Create Account & Credit Balance
                </button>
              </form>
            </div>
          </div>
        )}

        {/* VIEW 3: TRANSFERS & CLEARING */}
        {activeTab === 'transfers' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Transfer Portal Form */}
            <div className="lg:col-span-7 bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <div className="flex justify-between items-start mb-1">
                <h2 className="text-lg font-bold text-white">Transfer & Payment Settlement</h2>
                <span className="px-2.5 py-0.5 rounded text-[11px] bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                  {transferType === 'instant' ? '⚡ Reflects Immediately' : '⏳ Queued Mode'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-5">
                Send funds between bank accounts with instant ledger reflection or batched queues
              </p>

              {/* Transfer Mode Selector */}
              <div className="grid grid-cols-3 gap-2 p-1 bg-slate-950 rounded-xl mb-6 text-xs font-semibold">
                {[
                  { id: 'instant', label: 'Instant Settlement', desc: 'Direct Ledger (Immediate)' },
                  { id: 'standard', label: 'Standard Clearing', desc: 'Circular Queue (FIFO)' },
                  { id: 'priority', label: 'Priority Wire / RTGS', desc: 'Min-Heap (Due Time)' }
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setTransferType(mode.id as any)}
                    className={`py-2 px-3 rounded-lg text-center transition cursor-pointer ${
                      transferType === mode.id
                        ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <div>{mode.label}</div>
                    <div className="text-[10px] font-normal opacity-75">{mode.desc}</div>
                  </button>
                ))}
              </div>

              {transferType === 'instant' && (
                <div className="bg-cyan-950/40 border border-cyan-800 p-3 rounded-xl mb-4 text-xs text-cyan-300 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>
                    <strong>Instant Settlement Mode:</strong> Debit and credit happen atomically right now, updating account balances and the ledger in real time.
                  </span>
                </div>
              )}
              {transferType === 'standard' && (
                <div className="bg-slate-950 border border-slate-800 p-3 rounded-xl mb-4 text-xs text-slate-300 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-400 shrink-0" />
                  <span>
                    <strong>Circular Queue FIFO Mode:</strong> Transaction is queued in the circular buffer. Click "Clear Next" or "Clear All" in the right sidebar to clear and reflect.
                  </span>
                </div>
              )}
              {transferType === 'priority' && (
                <div className="bg-amber-950/40 border border-amber-800 p-3 rounded-xl mb-4 text-xs text-amber-300 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>
                    <strong>Priority Min-Heap Mode:</strong> Transaction is prioritized by earliest scheduled due time. Click "Clear Earliest" to execute by priority.
                  </span>
                </div>
              )}

              <form onSubmit={handleExecuteTransfer} className="space-y-4 text-xs">
                {/* Source Account */}
                <div>
                  <label className="block text-slate-400 mb-1">Source Account (Sender):</label>
                  <select
                    value={fromAcc}
                    onChange={(e) => setFromAcc(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  >
                    {accounts.map((a) => (
                      <option key={a.account_number} value={a.account_number}>
                        A/C {a.account_number} - {a.holder_name} (Available: ₹{a.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Destination Account with Quick Selection */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-slate-400">Destination Account (Recipient):</label>
                    <span className="text-[11px] text-cyan-400">Quick-select existing account:</span>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      required
                      placeholder="Enter recipient account number (e.g. 102)"
                      value={toAcc}
                      onChange={(e) => setToAcc(e.target.value)}
                      className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                    />
                    <select
                      value=""
                      onChange={(e) => {
                        if (e.target.value) setToAcc(e.target.value);
                      }}
                      className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-slate-300 text-xs focus:outline-none"
                    >
                      <option value="">Choose Recipient...</option>
                      {accounts
                        .filter((a) => a.account_number !== fromAcc)
                        .map((a) => (
                          <option key={a.account_number} value={a.account_number}>
                            A/C {a.account_number} ({a.holder_name})
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                {/* Amount and Schedule */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-slate-400 mb-1">Transfer Amount (INR ₹):</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0.01"
                      required
                      placeholder="0.00"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  {transferType === 'priority' && (
                    <div>
                      <label className="block text-slate-400 mb-1">Scheduled Window (Minutes):</label>
                      <input
                        type="number"
                        min="1"
                        value={dueMins}
                        onChange={(e) => setDueMins(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Payment Reference / Narration:</label>
                  <input
                    type="text"
                    placeholder="e.g. Monthly Consultant Invoice"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg transition shadow-lg shadow-cyan-600/20 text-sm mt-2 cursor-pointer"
                >
                  {transferType === 'instant' ? '⚡ Execute & Settle Transfer Immediately' : 'Submit & Queue Transaction'}
                </button>
              </form>
            </div>

            {/* Clearing Queues Sidebar */}
            <div className="lg:col-span-5 space-y-6">
              {/* Batch Processing Master Button */}
              <div className="bg-slate-900 p-4 rounded-2xl border border-slate-800 flex justify-between items-center">
                <div>
                  <h4 className="text-xs font-bold text-white">Batch Clearing Engine</h4>
                  <p className="text-[11px] text-slate-400">
                    {queues.regular_queue.length + queues.priority_queue.length} total pending transfers
                  </p>
                </div>
                <button
                  onClick={handleProcessAll}
                  disabled={queues.regular_queue.length === 0 && queues.priority_queue.length === 0}
                  className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-lg text-xs font-bold transition cursor-pointer"
                >
                  ⚡ Clear All Queued
                </button>
              </div>

              {/* Regular Queue (Circular FIFO) */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">Pending Regular Transfers</h3>
                    <p className="text-[11px] text-slate-400">Circular Queue (FIFO) clearing</p>
                  </div>
                  <button
                    onClick={handleProcessRegular}
                    disabled={queues.regular_queue.length === 0}
                    className="text-xs px-2.5 py-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded font-medium cursor-pointer"
                  >
                    Clear Next
                  </button>
                </div>

                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {queues.regular_queue.map((tx) => (
                    <div key={tx.tx_id} className="p-2.5 bg-slate-800/60 rounded-lg text-xs flex justify-between items-center">
                      <div>
                        <div className="font-semibold text-white">{tx.tx_id}</div>
                        <div className="text-[11px] text-slate-400">
                          {tx.from_account} ➔ {tx.to_account || '—'}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-emerald-400 font-bold">
                          ₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </div>
                        <span className="text-[9px] bg-slate-700 px-1.5 py-0.2 rounded text-slate-300">QUEUED</span>
                      </div>
                    </div>
                  ))}
                  {queues.regular_queue.length === 0 && (
                    <div className="text-center py-4 text-xs text-slate-500">Regular clearing queue is empty.</div>
                  )}
                </div>
              </div>

              {/* Priority Wire Queue (Min-Heap) */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">Scheduled Priority Wires</h3>
                    <p className="text-[11px] text-slate-400">Binary Min-Heap earliest-due clearing</p>
                  </div>
                  <button
                    onClick={handleProcessPriority}
                    disabled={queues.priority_queue.length === 0}
                    className="text-xs px-2.5 py-1 bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white rounded font-medium cursor-pointer"
                  >
                    Clear Earliest
                  </button>
                </div>

                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {queues.priority_queue.map((tx) => (
                    <div key={tx.tx_id} className="p-2.5 bg-slate-800/60 rounded-lg text-xs flex justify-between items-center">
                      <div>
                        <div className="font-semibold text-white">{tx.tx_id}</div>
                        <div className="text-[11px] text-amber-300/80">Due: {tx.due_time.split(' ')[1]}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-emerald-400 font-bold">
                          ₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </div>
                        <span className="text-[9px] bg-amber-950 text-amber-300 border border-amber-800 px-1.5 py-0.2 rounded">
                          PRIORITY
                        </span>
                      </div>
                    </div>
                  ))}
                  {queues.priority_queue.length === 0 && (
                    <div className="text-center py-4 text-xs text-slate-500">No scheduled priority wires.</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 4: OFFICIAL STATEMENTS & PDF DOWNLOAD */}
        {activeTab === 'statements' && (
          <div className="space-y-6">
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-bold text-white">Official Bank Statement Center</h2>
                  <p className="text-xs text-slate-400 mt-1">Audit-ready statements formatted strictly per commercial banking regulations</p>
                </div>

                {/* PDF Download Trigger */}
                <div className="flex flex-wrap items-center gap-3">
                  <select
                    value={stmtAccount}
                    onChange={(e) => setStmtAccount(e.target.value)}
                    className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
                  >
                    {accounts.map((a) => (
                      <option key={a.account_number} value={a.account_number}>
                        A/C {a.account_number} - {a.holder_name}
                      </option>
                    ))}
                  </select>

                  <select
                    value={stmtDays}
                    onChange={(e) => setStmtDays(Number(e.target.value))}
                    className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white"
                  >
                    <option value={7}>Last 7 Days</option>
                    <option value={30}>Last 30 Days</option>
                    <option value={90}>Last 90 Days</option>
                    <option value={365}>Full Year</option>
                  </select>

                  <button
                    onClick={() => {
                      if (stmtAccount) {
                        window.open(api.getPdfStatementUrl(stmtAccount, stmtDays), '_blank');
                      }
                    }}
                    className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-lg text-xs flex items-center space-x-2 shadow-lg shadow-emerald-600/20 cursor-pointer"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Official PDF Statement</span>
                  </button>
                </div>
              </div>

              {/* Statement Preview Table */}
              <div className="mt-6">
                <div className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">
                  Ledger Transactions Preview (Account {stmtAccount})
                </div>
                <div className="overflow-x-auto border border-slate-800 rounded-xl">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                      <tr>
                        <th className="p-3">Posting Date</th>
                        <th className="p-3">Narration / Description</th>
                        <th className="p-3">Reference No.</th>
                        <th className="p-3">Type</th>
                        <th className="p-3 text-right">Debit (Dr)</th>
                        <th className="p-3 text-right">Credit (Cr)</th>
                        <th className="p-3 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-900/60">
                      {history
                        .filter((tx) => tx.from_account === stmtAccount || tx.to_account === stmtAccount)
                        .map((tx) => {
                          const isCredit = tx.type === 'DEPOSIT' || (tx.type === 'TRANSFER' && tx.to_account === stmtAccount);
                          const isDebit = tx.type === 'WITHDRAWAL' || (tx.type === 'TRANSFER' && tx.from_account === stmtAccount);
                          return (
                            <tr key={tx.tx_id} className="hover:bg-slate-800/40">
                              <td className="p-3 text-slate-300">{tx.timestamp}</td>
                              <td className="p-3 text-white font-medium max-w-xs truncate">
                                {tx.description || `${tx.type} transaction`}
                              </td>
                              <td className="p-3 font-mono text-cyan-400">{tx.tx_id}</td>
                              <td className="p-3">{tx.type}</td>
                              <td className="p-3 text-right font-mono text-rose-400">
                                {isDebit ? `₹${tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                              </td>
                              <td className="p-3 text-right font-mono text-emerald-400">
                                {isCredit ? `₹${tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                              </td>
                              <td className="p-3 text-center">
                                <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">
                                  {tx.status}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      {history.filter((tx) => tx.from_account === stmtAccount || tx.to_account === stmtAccount).length === 0 && (
                        <tr>
                          <td colSpan={7} className="p-8 text-center text-slate-500">
                            No transactions recorded for Account {stmtAccount} during this period.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 5: ANTI-FRAUD & NETWORK (GRAPH ANALYSIS) */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <h2 className="text-xl font-bold text-white mb-1">Anti-Money Laundering & Graph Fraud Engine</h2>
              <p className="text-xs text-slate-400 mb-6">
                Direct traversal of fund movements using Directed Graph Breadth-First Search (BFS) and Depth-First Search (DFS)
              </p>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* BFS Section */}
                <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-4">
                  <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs uppercase">
                    <Network className="w-4 h-4" />
                    <span>BFS Counterparty Reachability Explorer</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Traces all multi-hop accounts connected via outgoing fund transfers from a target account.
                  </p>

                  <div className="flex gap-2">
                    <select
                      value={bfsAccount}
                      onChange={(e) => setBfsAccount(e.target.value)}
                      className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white flex-1"
                    >
                      {accounts.map((a) => (
                        <option key={a.account_number} value={a.account_number}>
                          A/C {a.account_number} ({a.holder_name})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={handleRunBfs}
                      className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold cursor-pointer"
                    >
                      Explore (BFS)
                    </button>
                  </div>

                  {bfsResults.length > 0 && (
                    <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 text-xs">
                      <div className="font-semibold text-white mb-2">
                        Connected Counterparties ({bfsResults.length}):
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {bfsResults.map((accNum) => (
                          <span
                            key={accNum}
                            className="px-2.5 py-1 bg-slate-800 border border-cyan-800 text-cyan-300 rounded font-mono text-xs"
                          >
                            A/C {accNum}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* DFS Cycles Section */}
                <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-4">
                  <div className="flex items-center space-x-2 text-rose-400 font-bold text-xs uppercase">
                    <AlertTriangle className="w-4 h-4" />
                    <span>DFS Circular Layering Loop Detection</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Scans all directed fund transfers across customer accounts to detect closed loops (e.g. Account A ➔ B ➔ C ➔ A) characteristic of suspicious layering.
                  </p>

                  <button
                    onClick={handleRunDfsCycles}
                    className="w-full py-2 px-4 bg-rose-600/80 hover:bg-rose-600 text-white rounded-lg text-xs font-bold transition cursor-pointer"
                  >
                    Run Circular Transfer Scan (DFS)
                  </button>

                  {fraudCycles.length > 0 && (
                    <div className="p-3 bg-rose-950/40 rounded-lg border border-rose-800 text-xs space-y-2">
                      <div className="font-bold text-rose-300 flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4" />
                        <span>{fraudCycles.length} Circular Money Loops Flagged:</span>
                      </div>
                      {fraudCycles.map((cycle, idx) => (
                        <div key={idx} className="font-mono text-[11px] text-white bg-slate-900/80 p-2 rounded border border-rose-900">
                          {cycle.join(' ➔ ')}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ===================================================================== */}
      {/* QUICK DEPOSIT MODAL */}
      {/* ===================================================================== */}
      {depositModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <ArrowDownLeft className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">Deposit Funds</h3>
              </div>
              <button onClick={() => setDepositModalOpen(false)} className="text-slate-400 hover:text-white cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Direct credit into A/C <strong className="text-white">{selectedAccount?.account_number}</strong> ({selectedAccount?.holder_name}).
            </p>
            <form onSubmit={handleDepositSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Deposit Amount (INR ₹):</label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  required
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setDepositModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-lg shadow-emerald-600/20 cursor-pointer"
                >
                  Confirm Deposit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* QUICK WITHDRAWAL MODAL */}
      {/* ===================================================================== */}
      {withdrawModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">Cash Withdrawal</h3>
              </div>
              <button onClick={() => setWithdrawModalOpen(false)} className="text-slate-400 hover:text-white cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Debit from A/C <strong className="text-white">{selectedAccount?.account_number}</strong> ({selectedAccount?.holder_name}). Available: <strong className="text-emerald-400 font-mono">₹{selectedAccount?.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
            </p>
            <form onSubmit={handleWithdrawSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Withdrawal Amount (INR ₹):</label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  required
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setWithdrawModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold shadow-lg shadow-amber-600/20 cursor-pointer"
                >
                  Confirm Withdrawal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* FOOTER */}
      {/* ===================================================================== */}
      <footer className="bg-slate-950 border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
          <div>NovaTrust Commercial Bank &copy; 2026. Built with manual Data Structures & Algorithms from first principles.</div>
          <div className="font-mono text-[11px] text-cyan-400">
            Hash Table • Circular Queue • Min-Heap • Doubly Linked List • Stack • AVL Tree • Graph
          </div>
        </div>
      </footer>
    </div>
  );
}
