export type TransactionType = 'DEPOSIT' | 'WITHDRAWAL' | 'TRANSFER';
export type TransactionStatus = 'PENDING' | 'COMPLETED' | 'FAILED' | 'UNDONE';

export interface Account {
  account_number: string;
  holder_name: string;
  balance: number;
  created_at: string;
}

export interface Transaction {
  tx_id: string;
  type: TransactionType;
  from_account: string;
  to_account: string;
  amount: number;
  timestamp: string;
  due_time: string;
  status: TransactionStatus;
  failure_reason: string;
  description: string;
}

export interface SystemStatus {
  status: string;
  total_accounts: number;
  total_balance: number;
  regular_queue_size: number;
  priority_queue_size: number;
  history_size: number;
  undo_stack_size: number;
  avl_tree_nodes: number;
  avl_tree_height: number;
  graph_transfers_count: number;
  hash_table_stats: {
    capacity: number;
    total_items: number;
    load_factor: number;
    non_empty_buckets: number;
    colliding_buckets: number;
    max_chain_length: number;
    avg_chain_length: number;
    resize_count: number;
  };
}

export interface LookupComparison {
  linear: {
    name: string;
    found: boolean;
    comparisons: number;
    time_ms: number;
    complexity: string;
  };
  binary: {
    name: string;
    found: boolean;
    comparisons: number;
    time_ms: number;
    complexity: string;
  };
  hash: {
    name: string;
    found: boolean;
    comparisons: number;
    time_ms: number;
    complexity: string;
  };
}

export interface DSAState {
  hash_table: {
    capacity: number;
    count: number;
    load_factor: number;
    max_load_factor: number;
    resize_count: number;
    active_buckets: Array<{
      bucket_index: number;
      chain_length: number;
      nodes: Array<{ key: string; holder: string; balance: number }>;
    }>;
  };
  circular_queue: {
    capacity: number;
    count: number;
    front: number;
    rear: number;
    slots: Array<{
      slot_index: number;
      has_item: boolean;
      tx_id: string | null;
      is_front: boolean;
      is_rear: boolean;
    }>;
  };
  min_heap: {
    size: number;
    nodes: Array<{
      index: number;
      key: string;
      tx_id: string;
      amount: number;
      parent_index: number | null;
    }>;
  };
  doubly_linked_list: {
    size: number;
    head_tx: string | null;
    tail_tx: string | null;
    sample_chain: Array<{
      index: number;
      tx_id: string;
      amount: number;
      has_prev: boolean;
      has_next: boolean;
    }>;
  };
  undo_stack: {
    depth: number;
    top_tx: string | null;
    frames: Array<{
      level: number;
      tx_id: string;
      type: string;
      amount: number;
    }>;
  };
  avl_tree: {
    total_nodes: number;
    total_entries: number;
    height: number;
  };
  graph: {
    total_accounts: number;
    total_transfers: number;
    edges: Array<{
      from: string;
      to: string;
      amount: number;
      tx_id: string;
      timestamp: string;
    }>;
  };
}
