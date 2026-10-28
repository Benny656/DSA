"""
Directed Graph implementation using Adjacency Lists.
Models fund transfers between accounts and performs:
- BFS: Exploration of reachable/connected accounts by transaction hops.
- DFS: Detection of suspicious circular transfer patterns (cycles) for fraud analysis.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class TransferEdge:
    """Represents a transfer edge between two accounts."""
    from_account: str
    to_account: str
    amount: float
    tx_id: str
    timestamp: str

    def to_dict(self):
        return {
            "from": self.from_account,
            "to": self.to_account,
            "amount": self.amount,
            "tx_id": self.tx_id,
            "timestamp": self.timestamp
        }


class TransactionGraph:
    """
    Directed Graph representing account fund transfers.
    Vertices = Account IDs.
    Edges = TransferEdge objects.
    """
    def __init__(self):
        # Adjacency list: account_id -> List[TransferEdge]
        self.adj_list: Dict[str, List[TransferEdge]] = {}
        # Keep track of all known vertices (including receivers with no outgoing edges)
        self.vertices: Set[str] = set()

    def add_vertex(self, account_id: str) -> None:
        """Add an account node to the graph."""
        if account_id not in self.adj_list:
            self.adj_list[account_id] = []
        self.vertices.add(account_id)

    def add_transfer(self, from_acc: str, to_acc: str, amount: float, tx_id: str, timestamp: str) -> None:
        """Add a directed fund transfer edge."""
        self.add_vertex(from_acc)
        self.add_vertex(to_acc)
        edge = TransferEdge(from_acc, to_acc, amount, tx_id, timestamp)
        self.adj_list[from_acc].append(edge)

    def remove_transfer(self, tx_id: str) -> bool:
        """Remove a transfer edge by tx_id (used during transaction undo)."""
        removed = False
        for edges in self.adj_list.values():
            initial_len = len(edges)
            edges[:] = [e for e in edges if e.tx_id != tx_id]
            if len(edges) < initial_len:
                removed = True
        return removed

    def get_neighbors(self, account_id: str) -> List[TransferEdge]:
        """Get outgoing transfer edges for an account."""
        return self.adj_list.get(account_id, [])

    def bfs_connected_accounts(self, start_account: str) -> List[Dict]:
        """
        Explore connected accounts starting from start_account using BFS.
        Returns visited accounts categorized by hop distance (degree of connection).
        """
        if start_account not in self.vertices:
            return []

        visited: Set[str] = {start_account}
        # Queue storing (account_id, hop_distance, path_of_edges)
        queue: List[Tuple[str, int, List[TransferEdge]]] = [(start_account, 0, [])]
        results = []

        while queue:
            curr_acc, hops, path = queue.pop(0)

            if hops > 0:
                results.append({
                    "account": curr_acc,
                    "hops": hops,
                    "path": [e.to_dict() for e in path]
                })

            for edge in self.get_neighbors(curr_acc):
                neighbor = edge.to_account
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, hops + 1, path + [edge]))

        return results

    def detect_circular_transfers(self) -> List[List[str]]:
        """
        Detect circular transfer patterns (directed cycles) using DFS.
        E.g., Account A -> Account B -> Account C -> Account A.
        Returns a list of cycle paths (e.g., ['101', '102', '103', '101']).
        """
        visited: Set[str] = set()
        recursion_stack: Dict[str, int] = {}  # account -> depth index in path
        current_path: List[str] = []
        cycles_found: List[List[str]] = []
        detected_cycle_sets: Set[Tuple[str, ...]] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            recursion_stack[node] = len(current_path)
            current_path.append(node)

            for edge in self.get_neighbors(node):
                neighbor = edge.to_account
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in recursion_stack:
                    # Cycle detected: from recursion_stack[neighbor] to end of current_path
                    start_idx = recursion_stack[neighbor]
                    cycle_nodes = current_path[start_idx:] + [neighbor]
                    # Canonical representation to avoid duplicate permutations of same cycle
                    core_cycle = cycle_nodes[:-1]
                    min_elem = min(core_cycle)
                    min_idx = core_cycle.index(min_elem)
                    canonical = tuple(core_cycle[min_idx:] + core_cycle[:min_idx])

                    if canonical not in detected_cycle_sets:
                        detected_cycle_sets.add(canonical)
                        cycles_found.append(cycle_nodes)

            current_path.pop()
            del recursion_stack[node]

        # Check all components in the graph
        for vertex in sorted(self.vertices):
            if vertex not in visited:
                dfs(vertex)

        return cycles_found

    def get_summary(self) -> Dict:
        """Return graph vertices and edges count summary."""
        total_edges = sum(len(edges) for edges in self.adj_list.values())
        return {
            "total_accounts": len(self.vertices),
            "total_transfers": total_edges
        }

    def clear(self) -> None:
        """Reset the graph."""
        self.adj_list.clear()
        self.vertices.clear()
