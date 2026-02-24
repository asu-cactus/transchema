"""
MCTSNode: the core data structure for MCTS-based schema transformation search.

Each node represents a partial transformation plan (operator sequence).
The tree built from MCTSNodes is the cross-iteration memory:
  - visit counts and accumulated rewards guide UCB1 selection
  - best scripts cached at each node for quick retrieval
"""

import math
from typing import Dict, List, Optional

# All operators the LLM can choose from (same as multi_step.py)
OPERATOR_TYPES: List[str] = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]

# Default UCB1 exploration constant (sqrt(2) ≈ 1.414)
DEFAULT_EXPLORATION_WEIGHT: float = 1.414


class MCTSNode:
    """
    A node in the MCTS tree.

    Represents the state S = (operation_history) — the ordered sequence of
    operators + configurations applied from the root to this node.

    Tree structure
    --------------
    - Keyed by operator_type (at most 6 children per node).
    - The actual configured operation string is stored in operation_history[-1].
    - Children are added lazily as MCTS iterations expand the tree.

    Memory across iterations
    ------------------------
    - visits / total_reward are updated by backpropagate() after every simulation.
    - UCB1 uses these accumulated stats to balance exploration vs exploitation.
    - best_script / best_score cache the highest-scoring result seen from this subtree.
    """

    def __init__(
        self,
        operation_history: List[str],
        parent: Optional["MCTSNode"] = None,
        operator_type: Optional[str] = None,
    ) -> None:
        # Transformation plan up to this point
        self.operation_history: List[str] = operation_history

        # Tree linkage
        self.parent: Optional["MCTSNode"] = parent
        self.operator_type: Optional[str] = operator_type  # action that led here

        # MCTS statistics (tree-based memory, mutated in-place across iterations)
        self.visits: int = 0
        self.total_reward: float = 0.0

        # Children keyed by operator_type string
        self.children: Dict[str, "MCTSNode"] = {}

        # Best result cached from any rollout passing through this subtree
        self.best_script: str = ""
        self.best_score: float = 0.0

        # A terminal node ends the operator sequence
        self.is_terminal: bool = (operator_type == "NO_MORE_OPERATION")

    # ──────────────────────────────────────────────────────────────────────────
    # UCB1 / selection helpers
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def q_value(self) -> float:
        """Average reward (exploitation term)."""
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    def ucb1(self, exploration_weight: float = DEFAULT_EXPLORATION_WEIGHT) -> float:
        """
        UCB1 score used by tree policy.
        Unexplored nodes return +inf so they are always tried first.
        """
        if self.visits == 0:
            return float("inf")
        if self.parent is None or self.parent.visits == 0:
            return float("inf")
        return self.q_value + exploration_weight * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

    def best_child(
        self, exploration_weight: float = DEFAULT_EXPLORATION_WEIGHT
    ) -> "MCTSNode":
        """Return the child with the highest UCB1 score."""
        return max(self.children.values(), key=lambda c: c.ucb1(exploration_weight))

    def is_fully_expanded(self) -> bool:
        """True when all 6 operator types have been tried as children."""
        return all(op in self.children for op in OPERATOR_TYPES)

    def untried_operators(self) -> List[str]:
        """Operator types not yet expanded from this node."""
        return [op for op in OPERATOR_TYPES if op not in self.children]

    # ──────────────────────────────────────────────────────────────────────────
    # Tree mutation
    # ──────────────────────────────────────────────────────────────────────────

    def add_child(
        self, operator_type: str, new_operation_history: List[str]
    ) -> "MCTSNode":
        """
        Expand a new child node for the given operator_type.
        Raises ValueError if this operator_type already has a child.
        """
        if operator_type in self.children:
            raise ValueError(
                f"Child for operator_type '{operator_type}' already exists. "
                "Use follow_child() to traverse an existing branch."
            )
        child = MCTSNode(
            operation_history=new_operation_history,
            parent=self,
            operator_type=operator_type,
        )
        self.children[operator_type] = child
        return child

    def update(self, reward: float) -> None:
        """Increment visit count and add reward (called during backpropagation)."""
        self.visits += 1
        self.total_reward += reward
        if reward > self.best_score:
            self.best_score = reward

    # ──────────────────────────────────────────────────────────────────────────
    # Serialization / inspection
    # ──────────────────────────────────────────────────────────────────────────

    def to_dict(self, depth: int = 0, max_depth: int = 8) -> dict:
        """Serialize the subtree for logging or persistence."""
        node_dict: dict = {
            "operator_type": self.operator_type,
            "operation_history": self.operation_history,
            "visits": self.visits,
            "q_value": round(self.q_value, 4),
            "best_score": round(self.best_score, 4),
            "is_terminal": self.is_terminal,
        }
        if depth < max_depth:
            node_dict["children"] = {
                k: v.to_dict(depth + 1, max_depth)
                for k, v in self.children.items()
            }
        return node_dict

    def best_path(self) -> List["MCTSNode"]:
        """
        Greedily descend the tree always picking the child with the highest
        Q-value (exploit only). Returns the path from self to a leaf.
        """
        path = [self]
        node = self
        while node.children:
            node = max(node.children.values(), key=lambda c: c.q_value)
            path.append(node)
        return path

    def __repr__(self) -> str:
        return (
            f"MCTSNode(op={self.operator_type}, "
            f"depth={len(self.operation_history)}, "
            f"visits={self.visits}, "
            f"q={self.q_value:.3f}, "
            f"children={list(self.children.keys())})"
        )
