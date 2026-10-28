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
  Sliders,
  Network,
  GitGraph,
  Calendar,
  Sparkles,
  Zap,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { Account, Transaction, SystemStatus, LookupComparison, DSAState } from '../types/bank';

export default function BankingApp() {
  // Navigation & View state
  const [activeTab, setActiveTab] = useState<'overview' | 'accounts' | 'transfers' | 'statements' | 'security'>('overview');
  const [dsaConsoleOpen, setDsaConsoleOpen] = useState(false);
  const [dsaActiveTab, setDsaActiveTab] = useState<'hashtable' | 'queue' | 'heap' | 'dll' | 'stack' | 'avl' | 'graph' | 'benchmarks'>('hashtable');

  // Core Data State
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [history, setHistory] = useState<Transaction[]>([]);
  const [queues, setQueues] = useState<{ regular_queue: Transaction[]; priority_queue: Transaction[] }>({ regular_queue: [], priority_queue: [] });
  const [dsaState, setDsaState] = useState<DSAState | null>(null);
  const [loading, setLoading] = useState(true);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // Form states
  const [transferType, setTransferType] = useState<'standard' | 'priority' | 'instant'>('standard');
  const [fromAcc, setFromAcc] = useState('');
  const [toAcc, setToAcc] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [dueMins, setDueMins] = useState('10');

  // Account creation form
  const [newAccNum, setNewAccNum] = useState('');
  const [newAccName, setNewAccName] = useState('');
  const [newAccBal, setNewAccBal] = useState('5000');

  // Statement Filters
  const [stmtAccount, setStmtAccount] = useState('');
  const [stmtDays, setStmtDays] = useState(30);

  // Security / Graph state
  const [bfsAccount, setBfsAccount] = useState('101');
  const [bfsResults, setBfsResults] = useState<any[]>([]);
  const [fraudCycles, setFraudCycles] = useState<string[][]>([]);

  // Search comparison state
  const [searchQuery, setSearchQuery] = useState('');
  const [lookupComp, setLookupComp] = useState<LookupComparison | null>(null);

  // Benchmark state
  const [benchSuite, setBenchSuite] = useState<'search' | 'sort'>('search');
  const [benchScale, setBenchScale] = useState<'fast' | 'full'>('fast');
  const [benchResults, setBenchResults] = useState<any>(null);
  const [benchLoading, setBenchLoading] = useState(false);

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

      if (accsData.length > 0 && !selectedAccount) {
        setSelectedAccount(accsData[0]);
        setFromAcc(accsData[0].account_number);
        setStmtAccount(accsData[0].account_number);
      }
    } catch (err: any) {
      console.error('Data load error:', err);
      showFeedback('error', 'Unable to connect to BankFlow backend. Please ensure api_server.py is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 6000);
    return () => clearInterval(interval);
  }, []);

  const showFeedback = (type: 'success' | 'error' | 'info', text: string) => {
    setFeedbackMsg({ type, text });
    setTimeout(() => setFeedbackMsg(null), 6000);
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

    try {
      if (transferType === 'instant') {
        const res = await api.transfer(fromAcc, toAcc, val, description || 'Instant Transfer');
        showFeedback('success', res.message);
      } else if (transferType === 'priority') {
        const mins = parseFloat(dueMins) || 10;
        const res = await api.queueTransaction('TRANSFER', fromAcc, toAcc, val, true, mins, description || `Priority Wire (Due in ${mins}m)`);
        showFeedback('success', res.message);
      } else {
        const res = await api.queueTransaction('TRANSFER', fromAcc, toAcc, val, false, 0, description || 'Standard Transfer');
        showFeedback('success', res.message);
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
      showFeedback('success', res.message);
      setNewAccNum('');
      setNewAccName('');
      setNewAccBal('5000');
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message || 'Failed to create account.');
    }
  };

  const handleDeposit = async () => {
    if (!selectedAccount) return;
    const val = prompt(`Enter deposit amount for Account ${selectedAccount.account_number}:`, '5000');
    if (!val) return;
    const amt = parseFloat(val);
    if (isNaN(amt) || amt <= 0) {
      alert('Invalid amount');
      return;
    }
    try {
      const res = await api.deposit(selectedAccount.account_number, amt, 'Over-the-counter deposit');
      showFeedback('success', res.message);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
    }
  };

  const handleWithdraw = async () => {
    if (!selectedAccount) return;
    const val = prompt(`Enter withdrawal amount for Account ${selectedAccount.account_number} (Available: ₹${selectedAccount.balance.toLocaleString('en-IN')}):`, '2000');
    if (!val) return;
    const amt = parseFloat(val);
    if (isNaN(amt) || amt <= 0) {
      alert('Invalid amount');
      return;
    }
    try {
      const res = await api.withdraw(selectedAccount.account_number, amt, 'ATM Cash Withdrawal');
      showFeedback('success', res.message);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
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
      showFeedback('success', res.message);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
    }
  };

  const handleProcessPriority = async () => {
    try {
      const res = await api.processNextPriority();
      showFeedback('success', res.message);
      await loadData();
    } catch (err: any) {
      showFeedback('error', err.message);
    }
  };

  const handleProcessAll = async () => {
    try {
      const res = await api.processAll();
      showFeedback('success', `Batch complete: ${res.processed_count} cleared, ${res.failed_count} failed.`);
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
    if (!searchQuery.trim()) return;
    try {
      const res = await api.compareLookup(searchQuery.trim());
      setLookupComp(res);
    } catch (err: any) {
      showFeedback('error', 'Lookup search failed.');
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
        showFeedback('error', `Security Alert: ${res.cycles.length} circular layering patterns detected!`);
      } else {
        showFeedback('success', 'Zero circular transfer loops detected in transfer network.');
      }
    } catch (err: any) {
      showFeedback('error', 'Cycle detection failed.');
    }
  };

  const handleRunBenchmarks = async () => {
    try {
      setBenchLoading(true);
      const res = await api.getPerformanceBenchmarks(benchSuite, benchScale);
      setBenchResults(res);
      showFeedback('success', 'Benchmark completed with time.perf_counter() metrics.');
    } catch (err: any) {
      showFeedback('error', 'Benchmark failed.');
    } finally {
      setBenchLoading(false);
    }
  };

  const handleQueryAvlRange = async () => {
    try {
      const s = parseFloat(avlStartHours) || 6;
      const e = parseFloat(avlEndHours) || 0;
      const res = await api.queryAvlRange(s, e);
      setAvlMatches(res.matches);
      showFeedback('info', `AVL Tree returned ${res.matches.length} matching transactions across date window.`);
    } catch (err: any) {
      showFeedback('error', 'AVL query failed.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* ===================================================================== */}
      {/* TOP HEADER / BRAND NAVIGATION */}
      {/* ===================================================================== */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white">NovaTrust</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-medium">COMMERCIAL</span>
              </div>
              <p className="text-xs text-slate-400">Institutional Banking & Digital Settlements</p>
            </div>
          </div>

          {/* Account Quick Selector & Actions */}
          <div className="flex items-center space-x-3">
            {/* Account dropdown */}
            <div className="hidden md:flex items-center bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-1.5 text-xs">
              <span className="text-slate-400 mr-2">Active Client:</span>
              <select
                className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
                value={selectedAccount?.account_number || ''}
                onChange={(e) => {
                  const acc = accounts.find((a) => a.account_number === e.target.value);
                  if (acc) {
                    setSelectedAccount(acc);
                    setFromAcc(acc.account_number);
                    setStmtAccount(acc.account_number);
                  }
                }}
              >
                {accounts.map((acc) => (
                  <option key={acc.account_number} value={acc.account_number} className="bg-slate-900 text-slate-200">
                    A/C {acc.account_number} • {acc.holder_name} (₹{acc.balance.toLocaleString('en-IN')})
                  </option>
                ))}
              </select>
            </div>

            {/* Reset Demo button */}
            <button
              onClick={handleResetDemo}
              className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition flex items-center space-x-1"
              title="Reset sample accounts and transactions"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>Reset Data</span>
            </button>

            {/* Prominent DSA Engine Inspector Toggle */}
            <button
              onClick={() => setDsaConsoleOpen(!dsaConsoleOpen)}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition flex items-center space-x-2 shadow-md ${
                dsaConsoleOpen
                  ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-orange-500/25'
                  : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/20'
              }`}
            >
              <Cpu className="w-4 h-4 animate-pulse" />
              <span>{dsaConsoleOpen ? 'Close DSA Inspector' : '⚡ DSA Engine Inspector'}</span>
              <span className="bg-white/20 px-1.5 py-0.5 rounded text-[10px]">7 DS</span>
            </button>
          </div>
        </div>

        {/* Global Feedback Banner */}
        {feedbackMsg && (
          <div
            className={`py-2 px-4 text-center text-xs font-medium border-t ${
              feedbackMsg.type === 'success'
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                : feedbackMsg.type === 'error'
                ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                : 'bg-blue-950/80 text-blue-300 border-blue-800'
            }`}
          >
            {feedbackMsg.text}
          </div>
        )}

        {/* Secondary Portal Navigation */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 border-t border-slate-800/80 py-1.5 overflow-x-auto text-sm">
          {[
            { id: 'overview', label: 'Dashboard & Portfolio', icon: TrendingUp },
            { id: 'accounts', label: 'Commercial Accounts', icon: CreditCard },
            { id: 'transfers', label: 'Transfers & Clearing', icon: ArrowLeftRight },
            { id: 'statements', label: 'Official Statements', icon: FileText },
            { id: 'security', label: 'Anti-Fraud & Network', icon: ShieldCheck }
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-medium transition ${
                  active
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </header>

      {/* ===================================================================== */}
      {/* COLLAPSIBLE / DEDICATED DSA ENGINE INSPECTOR & CONTROL LAB */}
      {/* ===================================================================== */}
      {dsaConsoleOpen && (
        <section className="bg-slate-900 border-b-2 border-cyan-500 shadow-2xl p-6 relative animate-in slide-in-from-top duration-200">
          <div className="max-w-7xl mx-auto">
            {/* Inspector Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-3">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
                  <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
                    Data Structures & Algorithms Live Controller & Diagnostic Engine
                  </h2>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Live state inspection of all custom first-principles data structures powering every banking operation.
                </p>
              </div>

              {/* Quick Execution Controls */}
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={handleProcessRegular}
                  className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow"
                >
                  <Zap className="w-3.5 h-3.5" />
                  <span>Step: Process FIFO</span>
                </button>
                <button
                  onClick={handleProcessPriority}
                  className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Step: Process Min-Heap</span>
                </button>
                <button
                  onClick={handleProcessAll}
                  className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Clear All Queues</span>
                </button>
                <button
                  onClick={handleUndoTransaction}
                  className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Execute Stack Rollback</span>
                </button>
              </div>
            </div>

            {/* Inspector Tabs */}
            <div className="flex space-x-2 py-3 overflow-x-auto text-xs border-b border-slate-800">
              {[
                { id: 'hashtable', label: '1. Hash Table (Separate Chaining)', badge: `${dsaState?.hash_table.count} keys` },
                { id: 'queue', label: '2. Circular Queue (FIFO)', badge: `${dsaState?.circular_queue.count} items` },
                { id: 'heap', label: '3. Binary Min-Heap (Priority)', badge: `${dsaState?.min_heap.size} items` },
                { id: 'dll', label: '4. Doubly Linked List', badge: `${dsaState?.doubly_linked_list.size} nodes` },
                { id: 'stack', label: '5. LIFO Stack (Undo)', badge: `${dsaState?.undo_stack.depth} frames` },
                { id: 'avl', label: '6. AVL Tree (Self-Balancing)', badge: `Height ${dsaState?.avl_tree.height}` },
                { id: 'graph', label: '7. Graph (BFS / DFS Cycles)', badge: `${dsaState?.graph.total_transfers} edges` },
                { id: 'benchmarks', label: '8. Benchmark Suite (O-Notation)', badge: 'perf_counter' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setDsaActiveTab(tab.id as any)}
                  className={`px-3 py-1.5 rounded-md font-medium whitespace-nowrap transition flex items-center space-x-1.5 ${
                    dsaActiveTab === tab.id
                      ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <span>{tab.label}</span>
                  <span className={`px-1.5 py-0.2 rounded text-[10px] ${dsaActiveTab === tab.id ? 'bg-black/20 text-slate-950' : 'bg-slate-900 text-cyan-400'}`}>
                    {tab.badge}
                  </span>
                </button>
              ))}
            </div>

            {/* Inspector Tab Content Area */}
            <div className="py-4">
              {/* TAB 1: HASH TABLE */}
              {dsaActiveTab === 'hashtable' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Current Table Capacity</div>
                      <div className="text-xl font-bold text-cyan-400 mt-1">{dsaState?.hash_table.capacity} buckets</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Total Key-Value Pairs</div>
                      <div className="text-xl font-bold text-emerald-400 mt-1">{dsaState?.hash_table.count} accounts</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Current Load Factor (λ)</div>
                      <div className="text-xl font-bold text-amber-400 mt-1">
                        {dsaState?.hash_table.load_factor} <span className="text-xs text-slate-500">(Max: 0.75)</span>
                      </div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Rehash / Resize Count</div>
                      <div className="text-xl font-bold text-purple-400 mt-1">{dsaState?.hash_table.resize_count} resizes</div>
                    </div>
                  </div>

                  {/* Bucket Visualizer */}
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                      Live Bucket Chains (Separate Chaining Collision Handling)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 max-h-64 overflow-y-auto">
                      {dsaState?.hash_table.active_buckets.map((b) => (
                        <div key={b.bucket_index} className="bg-slate-900 border border-slate-800 rounded p-2.5 text-xs">
                          <div className="flex justify-between items-center text-slate-400 mb-1.5 pb-1 border-b border-slate-800">
                            <span className="font-mono text-cyan-400">Bucket #{b.bucket_index}</span>
                            <span className="bg-slate-800 px-1.5 py-0.5 rounded text-[10px] text-slate-300">
                              Chain: {b.chain_length}
                            </span>
                          </div>
                          <div className="space-y-1">
                            {b.nodes.map((n, i) => (
                              <div key={i} className="bg-slate-800/60 p-1.5 rounded flex justify-between items-center text-[11px]">
                                <span className="font-semibold text-white">A/C {n.key}</span>
                                <span className="text-slate-400">{n.holder}</span>
                                <span className="text-emerald-400 font-mono">₹{n.balance.toLocaleString('en-IN')}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: CIRCULAR QUEUE */}
              {dsaActiveTab === 'queue' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Circular Buffer Capacity</div>
                      <div className="text-xl font-bold text-cyan-400 mt-1">{dsaState?.circular_queue.capacity} slots</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Current Items Count</div>
                      <div className="text-xl font-bold text-emerald-400 mt-1">{dsaState?.circular_queue.count} items</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Front Pointer Index</div>
                      <div className="text-xl font-bold text-amber-400 mt-1 font-mono">Index {dsaState?.circular_queue.front}</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Rear Pointer Index</div>
                      <div className="text-xl font-bold text-purple-400 mt-1 font-mono">Index {dsaState?.circular_queue.rear}</div>
                    </div>
                  </div>

                  {/* Visual Circular Slots Grid */}
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                        Circular Array Slots (Modular Arithmetic: (index + 1) % capacity)
                      </h3>
                      <div className="flex items-center space-x-3 text-[11px]">
                        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-emerald-500"></span> Front Pointer</span>
                        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-blue-500"></span> Rear Pointer</span>
                        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-slate-700"></span> Empty Slot</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 sm:grid-cols-8 md:grid-cols-16 gap-2">
                      {dsaState?.circular_queue.slots.map((s) => (
                        <div
                          key={s.slot_index}
                          className={`p-2 rounded border text-center transition ${
                            s.is_front
                              ? 'bg-emerald-950/70 border-emerald-500 text-emerald-300 ring-2 ring-emerald-500/30'
                              : s.is_rear
                              ? 'bg-blue-950/70 border-blue-500 text-blue-300 ring-2 ring-blue-500/30'
                              : s.has_item
                              ? 'bg-slate-800 border-slate-600 text-white'
                              : 'bg-slate-900 border-slate-800 text-slate-600'
                          }`}
                        >
                          <div className="text-[10px] font-mono text-slate-400">#{s.slot_index}</div>
                          <div className="text-xs font-bold mt-1 truncate">
                            {s.tx_id || '—'}
                          </div>
                          {s.is_front && <div className="text-[9px] font-bold text-emerald-400">FRONT</div>}
                          {s.is_rear && <div className="text-[9px] font-bold text-blue-400">REAR</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: BINARY MIN-HEAP */}
              {dsaActiveTab === 'heap' && (
                <div className="space-y-4">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                      Priority Binary Min-Heap Array (Earliest Due Time at Root)
                    </h3>
                    <p className="text-xs text-slate-400 mb-3">
                      Maintains min-heap property: parent(i) = (i - 1) // 2. High priority RTGS/Wires bubble up via _shift_up in O(log N).
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {dsaState?.min_heap.nodes.map((n) => (
                        <div key={n.index} className="bg-slate-900 border border-slate-800 p-3 rounded-lg text-xs">
                          <div className="flex justify-between items-center text-slate-400 pb-1 mb-1 border-b border-slate-800">
                            <span className="text-amber-400 font-bold font-mono">Heap Index #{n.index}</span>
                            <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-300">
                              Parent: {n.parent_index !== null ? `#${n.parent_index}` : 'ROOT'}
                            </span>
                          </div>
                          <div className="flex justify-between items-center mt-2">
                            <span className="font-semibold text-white">{n.tx_id}</span>
                            <span className="text-emerald-400 font-mono">₹{n.amount.toLocaleString('en-IN')}</span>
                          </div>
                          <div className="text-[11px] text-slate-400 mt-1">
                            Due Time: <span className="text-cyan-300 font-mono">{n.key}</span>
                          </div>
                        </div>
                      ))}
                      {dsaState?.min_heap.nodes.length === 0 && (
                        <div className="col-span-3 text-center py-6 text-slate-500 text-xs">
                          No pending priority transactions currently in Min-Heap.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: DOUBLY LINKED LIST */}
              {dsaActiveTab === 'dll' && (
                <div className="space-y-4">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                        Doubly Linked List Bidirectional History Chain (prev ⇄ next)
                      </h3>
                      <div className="text-xs text-cyan-400 font-mono">
                        Head: {dsaState?.doubly_linked_list.head_tx || 'None'} | Tail: {dsaState?.doubly_linked_list.tail_tx || 'None'}
                      </div>
                    </div>
                    <p className="text-xs text-slate-400 mb-3">
                      O(1) tail appends for incoming settlements. Backward traversal from tail directly generates mini-statements.
                    </p>

                    <div className="flex items-center space-x-2 overflow-x-auto py-2">
                      {dsaState?.doubly_linked_list.sample_chain.map((c, i) => (
                        <React.Fragment key={c.index}>
                          <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg min-w-[130px] text-xs shrink-0 shadow">
                            <div className="text-[10px] font-mono text-cyan-400 font-bold">Node #{c.index}</div>
                            <div className="font-semibold text-white mt-1">{c.tx_id}</div>
                            <div className="text-emerald-400 font-mono text-[11px]">₹{c.amount.toLocaleString('en-IN')}</div>
                          </div>
                          {i < (dsaState?.doubly_linked_list.sample_chain.length || 0) - 1 && (
                            <span className="text-slate-600 font-bold text-sm shrink-0">⇄</span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: LIFO UNDO STACK */}
              {dsaActiveTab === 'stack' && (
                <div className="space-y-4">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                        LIFO Transaction Rollback Stack
                      </h3>
                      <span className="text-xs text-rose-400 font-mono">Top Item: {dsaState?.undo_stack.top_tx || 'EMPTY'}</span>
                    </div>
                    <p className="text-xs text-slate-400 mb-3">
                      Pops the latest completed transaction and safely reverses ledger balances atomically while verifying account solvency.
                    </p>

                    <div className="space-y-2 max-w-md">
                      {dsaState?.undo_stack.frames.map((f, i) => (
                        <div
                          key={f.level}
                          className={`p-2.5 rounded border flex justify-between items-center text-xs ${
                            i === 0
                              ? 'bg-rose-950/60 border-rose-600 text-rose-200'
                              : 'bg-slate-900 border-slate-800 text-slate-300'
                          }`}
                        >
                          <div>
                            <span className="font-mono text-[10px] text-slate-400 mr-2">Frame #{f.level}</span>
                            <span className="font-bold">{f.tx_id}</span>
                            <span className="text-slate-400 ml-2">({f.type})</span>
                          </div>
                          <span className="font-mono font-semibold">₹{f.amount.toLocaleString('en-IN')}</span>
                          {i === 0 && <span className="bg-rose-600 text-white text-[10px] px-1.5 py-0.5 rounded font-bold">TOP</span>}
                        </div>
                      ))}
                      {dsaState?.undo_stack.frames.length === 0 && (
                        <div className="text-slate-500 text-xs py-4 text-center">Stack is currently empty.</div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 6: AVL TREE */}
              {dsaActiveTab === 'avl' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-3 text-xs">
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Total Unique Timestamps</div>
                      <div className="text-xl font-bold text-cyan-400 mt-1">{dsaState?.avl_tree.total_nodes} nodes</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Tree Height (Self-Balancing)</div>
                      <div className="text-xl font-bold text-emerald-400 mt-1">{dsaState?.avl_tree.height} levels</div>
                    </div>
                    <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700">
                      <div className="text-slate-400">Search Complexity</div>
                      <div className="text-xl font-bold text-purple-400 mt-1 font-mono">O(log N + K)</div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                      Test AVL Tree Range Search
                    </h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs mb-3">
                      <label className="text-slate-400">Start Hours Ago:</label>
                      <input
                        type="number"
                        className="bg-slate-900 border border-slate-700 rounded px-2 py-1 w-20 text-white"
                        value={avlStartHours}
                        onChange={(e) => setAvlStartHours(e.target.value)}
                      />
                      <label className="text-slate-400">End Hours Ago:</label>
                      <input
                        type="number"
                        className="bg-slate-900 border border-slate-700 rounded px-2 py-1 w-20 text-white"
                        value={avlEndHours}
                        onChange={(e) => setAvlEndHours(e.target.value)}
                      />
                      <button
                        onClick={handleQueryAvlRange}
                        className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium"
                      >
                        Execute Range Search
                      </button>
                    </div>

                    {avlMatches.length > 0 && (
                      <div className="border border-slate-800 rounded-lg overflow-hidden">
                        <table className="w-full text-xs text-left">
                          <thead className="bg-slate-900 text-slate-400 font-semibold border-b border-slate-800">
                            <tr>
                              <th className="p-2">Tx ID</th>
                              <th className="p-2">Type</th>
                              <th className="p-2">From</th>
                              <th className="p-2">To</th>
                              <th className="p-2">Amount</th>
                              <th className="p-2">Timestamp</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800">
                            {avlMatches.map((m) => (
                              <tr key={m.tx_id} className="hover:bg-slate-900/50">
                                <td className="p-2 font-mono text-cyan-400">{m.tx_id}</td>
                                <td className="p-2">{m.type}</td>
                                <td className="p-2">{m.from_account}</td>
                                <td className="p-2">{m.to_account || '—'}</td>
                                <td className="p-2 font-mono text-emerald-400">₹{m.amount.toLocaleString('en-IN')}</td>
                                <td className="p-2 text-slate-400">{m.timestamp}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 7: GRAPH */}
              {dsaActiveTab === 'graph' && (
                <div className="space-y-4">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                      Adjacency-List Directed Graph (Fund Transfer Topology)
                    </h3>
                    <div className="flex gap-2 mb-3">
                      <button onClick={handleRunDfsCycles} className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold">
                        Trigger DFS Circular Cycle Detection
                      </button>
                    </div>

                    {fraudCycles.length > 0 && (
                      <div className="p-3 bg-rose-950/60 border border-rose-600 rounded-lg text-xs mb-3 text-rose-200">
                        <div className="font-bold flex items-center gap-1.5 mb-1 text-rose-400">
                          <AlertTriangle className="w-4 h-4" /> Detected Circular Layering Pattern:
                        </div>
                        {fraudCycles.map((c, i) => (
                          <div key={i} className="font-mono text-white mt-1 bg-black/40 p-2 rounded">
                            Cycle #{i + 1}: {c.join(' ➔ ')}
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="text-xs text-slate-400 mb-1">Active Transfer Edges:</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-h-48 overflow-y-auto">
                      {dsaState?.graph.edges.map((e, i) => (
                        <div key={i} className="bg-slate-900 border border-slate-800 p-2 rounded text-xs">
                          <div className="text-slate-300 font-mono">
                            {e.from} <span className="text-cyan-400">➔</span> {e.to}
                          </div>
                          <div className="text-emerald-400 font-mono mt-0.5">₹{e.amount.toLocaleString('en-IN')}</div>
                          <div className="text-[10px] text-slate-500">{e.tx_id}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 8: BENCHMARKS */}
              {dsaActiveTab === 'benchmarks' && (
                <div className="space-y-4">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                      Empirical Performance Benchmarks (time.perf_counter)
                    </h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs mb-4">
                      <select
                        value={benchSuite}
                        onChange={(e) => setBenchSuite(e.target.value as any)}
                        className="bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-white"
                      >
                        <option value="search">Search: Linear O(N) vs Binary O(log N) vs Hash Table O(1)</option>
                        <option value="sort">Sort: Merge Sort O(N log N) vs Quick Sort O(N log N)</option>
                      </select>
                      <button
                        onClick={handleRunBenchmarks}
                        disabled={benchLoading}
                        className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded font-bold"
                      >
                        {benchLoading ? 'Benchmarking Datasets...' : 'Run Empirical Test'}
                      </button>
                    </div>

                    {benchResults && (
                      <div className="border border-slate-800 rounded-lg overflow-hidden text-xs">
                        <table className="w-full text-left">
                          <thead className="bg-slate-900 text-slate-400 font-semibold border-b border-slate-800">
                            <tr>
                              <th className="p-2">Dataset Size (N)</th>
                              {benchSuite === 'search' ? (
                                <>
                                  <th className="p-2 text-rose-400">Linear O(N)</th>
                                  <th className="p-2 text-blue-400">Binary O(log N)</th>
                                  <th className="p-2 text-emerald-400">Hash Table O(1)</th>
                                </>
                              ) : (
                                <>
                                  <th className="p-2 text-purple-400">Merge Sort (ms)</th>
                                  <th className="p-2 text-cyan-400">Quick Sort (ms)</th>
                                </>
                              )}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800">
                            {benchResults.sizes.map((s: number, i: number) => (
                              <tr key={s} className="hover:bg-slate-900/50">
                                <td className="p-2 font-mono font-bold text-white">{s.toLocaleString()} records</td>
                                {benchSuite === 'search' ? (
                                  <>
                                    <td className="p-2 font-mono text-rose-300">
                                      {benchResults.linear_ms[i]} ms ({benchResults.linear_comparisons[i]} comp)
                                    </td>
                                    <td className="p-2 font-mono text-blue-300">
                                      {benchResults.binary_ms[i]} ms ({benchResults.binary_comparisons[i]} comp)
                                    </td>
                                    <td className="p-2 font-mono text-emerald-300 font-bold">
                                      {benchResults.hash_ms[i]} ms ({benchResults.hash_comparisons[i]} comp)
                                    </td>
                                  </>
                                ) : (
                                  <>
                                    <td className="p-2 font-mono text-purple-300">{benchResults.merge_ms[i]} ms</td>
                                    <td className="p-2 font-mono text-cyan-300">{benchResults.quick_ms[i]} ms</td>
                                  </>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ===================================================================== */}
      {/* MAIN BANKING INTERFACE (AUTHENTIC COMMERCIAL BANKING EXPERIENCE) */}
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
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Total Portfolio Wealth</span>
                    <div className="flex items-center space-x-3 mt-1.5">
                      <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                        {hideBalance ? '••••••••' : `₹${(status?.total_balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
                      </h1>
                      <button onClick={() => setHideBalance(!hideBalance)} className="text-slate-400 hover:text-slate-200">
                        {hideBalance ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                      </button>
                    </div>
                    <div className="flex items-center space-x-2 mt-2 text-xs text-emerald-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                      <span>Verified Ledger Balance across {accounts.length} Institutional Accounts</span>
                    </div>
                  </div>

                  {/* Primary Account Card Badge */}
                  <div className="bg-gradient-to-tr from-cyan-600 to-blue-600 text-white p-3.5 rounded-xl shadow-lg shadow-cyan-600/20 text-right hidden sm:block">
                    <div className="text-[10px] tracking-wider uppercase opacity-80">Primary Account</div>
                    <div className="text-base font-bold font-mono">A/C {selectedAccount?.account_number}</div>
                    <div className="text-xs opacity-90">{selectedAccount?.holder_name}</div>
                  </div>
                </div>

                {/* Quick Action Ribbon */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-slate-800/80">
                  <button
                    onClick={() => setActiveTab('transfers')}
                    className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/80 border border-slate-700 text-left transition group"
                  >
                    <ArrowUpRight className="w-5 h-5 text-cyan-400 mb-1 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
                    <div className="text-xs font-semibold text-white">Send Money</div>
                    <div className="text-[11px] text-slate-400">Domestic & Wire</div>
                  </button>

                  <button
                    onClick={handleDeposit}
                    className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/80 border border-slate-700 text-left transition group"
                  >
                    <ArrowDownLeft className="w-5 h-5 text-emerald-400 mb-1 group-hover:translate-y-0.5 transition" />
                    <div className="text-xs font-semibold text-white">Deposit Funds</div>
                    <div className="text-[11px] text-slate-400">Direct Credit</div>
                  </button>

                  <button
                    onClick={handleWithdraw}
                    className="p-3 rounded-xl bg-slate-800/70 hover:bg-slate-700/80 border border-slate-700 text-left transition group"
                  >
                    <CreditCard className="w-5 h-5 text-amber-400 mb-1" />
                    <div className="text-xs font-semibold text-white">Cash Withdrawal</div>
                    <div className="text-[11px] text-slate-400">ATM / Branch</div>
                  </button>

                  <button
                    onClick={() => {
                      if (selectedAccount) {
                        window.open(api.getPdfStatementUrl(selectedAccount.account_number, 30), '_blank');
                      }
                    }}
                    className="p-3 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800 text-left transition group"
                  >
                    <Download className="w-5 h-5 text-cyan-400 mb-1" />
                    <div className="text-xs font-semibold text-white">Download PDF</div>
                    <div className="text-[11px] text-cyan-300/80">Official Statement</div>
                  </button>
                </div>
              </div>

              {/* Digital Commercial Platinum Card Widget */}
              <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6 rounded-2xl border border-indigo-900/60 shadow-xl flex flex-col justify-between text-white relative overflow-hidden">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[11px] font-semibold tracking-widest text-cyan-300">NOVATRUST PLATINUM</span>
                    <div className="text-xs text-slate-400">Commercial Business Debit</div>
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
                  <span className="text-emerald-400 font-medium">● ACTIVE & SECURE</span>
                  <span className="text-slate-400 font-mono">CVV: ***</span>
                </div>
              </div>
            </div>

            {/* Middle Section: Recent Transactions & Active Accounts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Activity Table (2 cols) */}
              <div className="lg:col-span-2 bg-slate-900 rounded-2xl border border-slate-800 p-6">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h2 className="text-base font-bold text-white">Recent Transaction Activity</h2>
                    <p className="text-xs text-slate-400">Chronological ledger of executed fund transfers</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('statements')}
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center space-x-1"
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
                      {history.slice(0, 6).map((tx) => (
                        <tr key={tx.tx_id} className="hover:bg-slate-800/30 transition">
                          <td className="py-3 font-mono font-medium text-cyan-400">{tx.tx_id}</td>
                          <td className="py-3 font-medium text-slate-200">{tx.type}</td>
                          <td className="py-3 text-slate-400">
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
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Account Quick List & Disputed Undo */}
              <div className="space-y-6">
                {/* Account list mini */}
                <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                  <h3 className="text-sm font-bold text-white mb-1">Your Accounts</h3>
                  <p className="text-xs text-slate-400 mb-4">Click to inspect or change active account</p>

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
                            ? 'bg-cyan-950/40 border-cyan-500/60 shadow-md'
                            : 'bg-slate-800/40 border-slate-800 hover:bg-slate-800'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-semibold text-xs text-white">{acc.holder_name}</span>
                          <span className="font-mono text-xs font-bold text-emerald-400">
                            ₹{acc.balance.toLocaleString('en-IN')}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1">A/C No: {acc.account_number}</div>
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
                    Dispute and safely roll back the most recent completed transaction.
                  </p>
                  <button
                    onClick={handleUndoTransaction}
                    className="w-full py-2 px-3 rounded-lg bg-rose-600/80 hover:bg-rose-600 text-white text-xs font-semibold transition"
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
                <p className="text-xs text-slate-400 mt-1">Verified institutional and savings deposit accounts</p>
              </div>

              {/* Search bar */}
              <div className="flex items-center space-x-2 w-full md:w-auto">
                <div className="relative flex-1 md:w-64">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search Account No..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <button
                  onClick={handleRunSearchLookup}
                  className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium"
                >
                  Lookup
                </button>
              </div>
            </div>

            {/* Lookup Comparison Banner if searched */}
            {lookupComp && (
              <div className="bg-slate-900 border border-cyan-800 p-4 rounded-xl text-xs space-y-2">
                <div className="font-bold text-cyan-400 flex items-center gap-2">
                  <Zap className="w-4 h-4" /> Account Lookup Verification Performance:
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                  <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400">Sequential Scanning</span>
                    <div className="text-sm font-bold text-rose-400">{lookupComp.linear.comparisons} comparisons</div>
                    <div className="text-[11px] text-slate-500 font-mono">{lookupComp.linear.time_ms.toFixed(4)} ms ({lookupComp.linear.complexity})</div>
                  </div>
                  <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400">Binary Search</span>
                    <div className="text-sm font-bold text-blue-400">{lookupComp.binary.comparisons} comparisons</div>
                    <div className="text-[11px] text-slate-500 font-mono">{lookupComp.binary.time_ms.toFixed(4)} ms ({lookupComp.binary.complexity})</div>
                  </div>
                  <div className="bg-slate-950 p-2.5 rounded border border-slate-800">
                    <span className="text-slate-400">Direct Hash Indexing</span>
                    <div className="text-sm font-bold text-emerald-400">{lookupComp.hash.comparisons} comparisons</div>
                    <div className="text-[11px] text-slate-500 font-mono">{lookupComp.hash.time_ms.toFixed(4)} ms ({lookupComp.hash.complexity})</div>
                  </div>
                </div>
              </div>
            )}

            {/* Accounts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {accounts.map((acc) => (
                <div key={acc.account_number} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-white text-base">{acc.holder_name}</h3>
                      <p className="text-xs text-slate-400 font-mono">A/C: {acc.account_number}</p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
                      VERIFIED
                    </span>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-end">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider">Available Balance</span>
                      <div className="text-xl font-bold font-mono text-emerald-400">
                        ₹{acc.balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        window.open(api.getPdfStatementUrl(acc.account_number, 30), '_blank');
                      }}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs text-cyan-300 font-medium flex items-center space-x-1"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>PDF</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Create Account Form */}
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 max-w-xl">
              <h3 className="text-base font-bold text-white mb-1 flex items-center gap-2">
                <PlusCircle className="w-5 h-5 text-cyan-400" /> Open New Commercial Account
              </h3>
              <p className="text-xs text-slate-400 mb-4">Register new corporate or retail customer in ledger</p>

              <form onSubmit={handleCreateAccount} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Account Number (Digits only):</label>
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
                    placeholder="e.g. Vikram Sharma"
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
                  className="w-full py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg transition"
                >
                  Create & Activate Account
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
              <h2 className="text-lg font-bold text-white mb-1">Transfer & Payment Settlement</h2>
              <p className="text-xs text-slate-400 mb-6">Execute inter-account fund transfers and commercial wire payments</p>

              {/* Transfer Mode Selector */}
              <div className="grid grid-cols-3 gap-2 p-1 bg-slate-950 rounded-xl mb-6 text-xs font-semibold">
                {[
                  { id: 'standard', label: 'Standard Clearing', desc: 'Batched Transfer' },
                  { id: 'priority', label: 'Priority Wire / RTGS', desc: 'Time-Scheduled' },
                  { id: 'instant', label: 'Instant Settlement', desc: 'Direct Ledger' }
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setTransferType(mode.id as any)}
                    className={`py-2 px-3 rounded-lg text-center transition ${
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

              <form onSubmit={handleExecuteTransfer} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Source Account:</label>
                  <select
                    value={fromAcc}
                    onChange={(e) => setFromAcc(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white"
                  >
                    {accounts.map((a) => (
                      <option key={a.account_number} value={a.account_number}>
                        A/C {a.account_number} - {a.holder_name} (Avail: ₹{a.balance.toLocaleString('en-IN')})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Destination Account Number:</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter recipient account number (e.g. 102)"
                    value={toAcc}
                    onChange={(e) => setToAcc(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>

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
                  <label className="block text-slate-400 mb-1">Payment Reference / Memo:</label>
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
                  className="w-full py-3 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-lg transition shadow-lg shadow-cyan-600/20 text-sm mt-2"
                >
                  {transferType === 'instant' ? 'Execute Instant Settlement' : 'Authorize & Submit Transfer'}
                </button>
              </form>
            </div>

            {/* Pending Clearing Queues Sidebar */}
            <div className="lg:col-span-5 space-y-6">
              {/* Regular Queue */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">Pending Regular Transfers</h3>
                    <p className="text-[11px] text-slate-400">{queues.regular_queue.length} transactions waiting in clearing queue</p>
                  </div>
                  <button
                    onClick={handleProcessRegular}
                    className="text-xs px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded font-medium"
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
                        <div className="font-mono text-emerald-400 font-bold">₹{tx.amount.toLocaleString('en-IN')}</div>
                        <span className="text-[9px] bg-slate-700 px-1.5 py-0.2 rounded text-slate-300">QUEUED</span>
                      </div>
                    </div>
                  ))}
                  {queues.regular_queue.length === 0 && (
                    <div className="text-center py-4 text-xs text-slate-500">Regular clearing queue is empty.</div>
                  )}
                </div>
              </div>

              {/* Priority Wire Queue */}
              <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">Scheduled Priority Wires</h3>
                    <p className="text-[11px] text-slate-400">{queues.priority_queue.length} urgent transfers scheduled</p>
                  </div>
                  <button
                    onClick={handleProcessPriority}
                    className="text-xs px-2.5 py-1 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium"
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
                        <div className="font-mono text-emerald-400 font-bold">₹{tx.amount.toLocaleString('en-IN')}</div>
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
                <div className="flex items-center space-x-3">
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
                    className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-lg text-xs flex items-center space-x-2 shadow-lg shadow-emerald-600/20"
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
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 5: SECURITY & ANTI-FRAUD CENTER */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
              <div className="flex items-center space-x-3 mb-2">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
                <h2 className="text-xl font-bold text-white">Banking Security & Anti-Fraud Center</h2>
              </div>
              <p className="text-xs text-slate-400">
                Continuous automated surveillance for suspicious circular transaction layering and money laundering rings.
              </p>

              {/* Fraud Detection Action */}
              <div className="mt-6 p-5 bg-gradient-to-r from-rose-950/40 via-slate-900 to-slate-900 rounded-xl border border-rose-900/60 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <div className="text-sm font-bold text-rose-300 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400" /> Automated Circular Layering Surveillance
                  </div>
                  <p className="text-xs text-slate-400 mt-1 max-w-xl">
                    Scans all directed fund transfers across customer accounts to detect closed loops (e.g. Account A ➔ B ➔ C ➔ A) characteristic of suspicious layering.
                  </p>
                </div>
                <button
                  onClick={handleRunDfsCycles}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-lg text-xs shadow-lg shadow-rose-600/20 whitespace-nowrap"
                >
                  Run Circular Transfer Scan
                </button>
              </div>

              {/* Flagged Rings */}
              {fraudCycles.length > 0 ? (
                <div className="mt-4 p-4 bg-rose-950/70 border border-rose-600 rounded-xl text-xs space-y-2">
                  <div className="font-bold text-rose-300">⚠️ {fraudCycles.length} Suspicious Circular Ring(s) Flagged:</div>
                  {fraudCycles.map((cycle, i) => (
                    <div key={i} className="bg-black/50 p-3 rounded-lg border border-rose-800 font-mono text-rose-200">
                      Loop #{i + 1}: {cycle.join(' ➔ ')}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="mt-4 p-4 bg-emerald-950/40 border border-emerald-800/80 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> No circular transaction anomalies flagged in the current settlement topology.
                </div>
              )}

              {/* Counterparty Network Trace (BFS) */}
              <div className="mt-8 pt-6 border-t border-slate-800">
                <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                  <Network className="w-4 h-4 text-cyan-400" /> Counterparty Network Trace
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Explore multi-degree fund transfer flows from a specific account.
                </p>

                <div className="flex items-center space-x-3 mb-4">
                  <input
                    type="text"
                    placeholder="Enter Account No (e.g. 101)"
                    value={bfsAccount}
                    onChange={(e) => setBfsAccount(e.target.value)}
                    className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white"
                  />
                  <button
                    onClick={handleRunBfs}
                    className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg"
                  >
                    Trace Counterparties
                  </button>
                </div>

                {bfsResults.length > 0 && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                    {bfsResults.map((item, idx) => (
                      <div key={idx} className="bg-slate-950 border border-slate-800 p-3 rounded-lg text-xs">
                        <div className="flex justify-between items-center text-slate-400">
                          <span className="font-bold text-white">Recipient: A/C {item.account}</span>
                          <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-cyan-400">
                            {item.hops} Degree Hop{item.hops > 1 ? 's' : ''}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ===================================================================== */}
      {/* FOOTER */}
      {/* ===================================================================== */}
      <footer className="border-t border-slate-800/80 bg-slate-900 py-4 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-2">
          <div>
            NovaTrust Commercial Bank • Educational Banking Platform & Algorithms Simulation
          </div>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>Powered by First-Principles Data Structures</span>
            <span>•</span>
            <span className="text-emerald-400 font-mono">FastAPI + Next.js</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
