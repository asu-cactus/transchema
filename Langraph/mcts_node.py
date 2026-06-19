"""
MCTSNode: the core data structure for MCTS-based schema transformation search.

Each node represents a partial transformation plan (pipeline prefix).
The tree built from MCTSNodes is the cross-iteration memory:
  - visit counts and accumulated rewards guide UCB1 selection
  - best scripts cached at each node for quick retrieval

Tree structure (key design decision)
--------------------------------------
Children are keyed by the FULL configured pipeline step string
(e.g. "JOIN : [[S0, S1]] columns=[[S0.id, S1.id]]"), NOT by operator type alone.

This means multiple different JOIN configurations can all be children of the
same parent node, and the tree correctly represents distinct partial pipelines
rather than just distinct operator types.

A node is "fully expanded" once it has MAX_CHILDREN children.  After that,
mcts_select descends past it using UCB1 to explore deeper plans.
"""

import math
from typing import Dict, List, Optional

# All operators the LLM can choose from (same as multi_step.py).
# Used by simulation, critique, and code-gen — GROUP_BY/AGGREGATE is a single step there.
OPERATOR_TYPES: List[str] = [
    "JOIN",
    "UNION",
    "GROUP_BY/AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]

# Operators used exclusively in the MCTS expansion layer.
# GROUP_BY and AGGREGATE are split into separate tree nodes so the MCTS can
# explore different aggregation variants independently under each GROUP_BY node.
# AGGREGATE may only appear as a child of a GROUP_BY node (enforced in next_operator_step).
EXPAND_OPERATOR_TYPES: List[str] = [
    "JOIN",
    "UNION",
    "GROUP_BY",
    "AGGREGATE",
    "PIVOT",
    "UNPIVOT",
    "NO_MORE_OPERATION",
]

# Structural operator types that standard nodes can have as children.
# A standard node is "fully expanded" once all of these types appear at least
# once among its children.
STRUCTURAL_EXPAND_OPS: List[str] = [
    "JOIN", "UNION", "GROUP_BY", "PIVOT", "UNPIVOT"
]

# Operator types required for an AGGREGATE node to be considered fully expanded.
# GROUP_BY is intentionally excluded: any operator (including GROUP_BY) is allowed
# after AGGREGATE, but the system must not MANDATE a GROUP_BY child — that would
# force unbounded GROUP_BY→AGGREGATE→GROUP_BY→... chains.
# The LLM may still freely propose GROUP_BY after AGGREGATE when it's appropriate.
POST_AGGREGATE_EXPAND_OPS: List[str] = [
    "JOIN", "UNION", "PIVOT", "UNPIVOT"
]


# Maximum number of AGGREGATE children a single GROUP_BY node may accumulate.
# Re-expansion beyond the initial batch is gated by the reaggregation_needed flag.
AGGREGATE_MAX_CHILDREN: int = 9

# Default UCB1 exploration constant (sqrt(2) ≈ 1.414)
DEFAULT_EXPLORATION_WEIGHT: float = 0.5


class MCTSNode:
    """
    A node in the MCTS tree.

    Represents the state S = (operation_history) — the ordered sequence of
    configured pipeline steps applied from the root to this node.

    Tree structure
    --------------
    - Children keyed by configured_step (full operation string, e.g.
      "JOIN : [[S0, S1]] columns=[...]").  Any number of distinct
      configurations of the SAME operator type can be children of the
      same parent, up to MAX_CHILDREN total.
    - The operator_type field is kept as human-readable metadata only.
    - Children are added lazily as MCTS iterations expand the tree.

    Memory across iterations
    ------------------------
    - visits / total_reward are updated by backpropagate() after every simulation.
    - UCB1 uses these accumulated stats to balance exploration vs exploitation.
    - best_script / best_score cache the highest-scoring result seen from this subtree.
    """

    # A node is considered "fully expanded" once it has this many children.
    # mcts_select will then descend past it into its children.
    MAX_CHILDREN: int = 3

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
        # operator_type is metadata (e.g. "JOIN") — NOT the children dict key
        self.operator_type: Optional[str] = operator_type

        # MCTS statistics (tree-based memory, mutated in-place across iterations)
        self.visits: int = 0
        self.total_reward: float = 0.0

        # Children keyed by configured_step (full pipeline step string)
        self.children: Dict[str, "MCTSNode"] = {}

        # Best result cached from any rollout passing through this subtree
        self.best_script: str = ""
        self.best_score: float = 0.0

        # A terminal node ends the operator sequence
        self.is_terminal: bool = (operator_type == "NO_MORE_OPERATION")

        # Set to True when the LLM can no longer suggest new configured steps
        # for this node (all candidates are already children). Once saturated,
        # is_fully_expanded() returns True so selection can descend past this node.
        self.saturated: bool = False

        # Set by backpropagate when this GROUP_BY node's subtree scores above the
        # reaggregation threshold AND there is still room for more AGGREGATE children.
        # mcts_select will pause descent here to trigger another expansion call,
        # then clears the flag.
        self.reaggregation_needed: bool = False

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
        """
        Criterion depends on this node's operator type:

        GROUP_BY: fully expanded once AGGREGATE_MAX_CHILDREN (9) AGGREGATE
            variants have been added. Until then, selection always stops here
            to add more aggregation candidates. The reaggregation_needed flag
            can trigger re-expansion past this threshold if the subtree is
            proving promising.

        AGGREGATE: fully expanded once every type in POST_AGGREGATE_EXPAND_OPS
            [JOIN, UNION, PIVOT, UNPIVOT] appears as a child. GROUP_BY is NOT
            required — it may appear if the LLM proposes it, but it is never
            mandated, preventing forced GROUP_BY→AGGREGATE→... chains.

        All other nodes: fully expanded once every type in STRUCTURAL_EXPAND_OPS
            appears at least once as a child's operator_type, OR when saturated.
        """
        if self.saturated:
            return True
        if self.operator_type == "GROUP_BY":
            return len(self.children) >= AGGREGATE_MAX_CHILDREN
        if self.operator_type == "AGGREGATE":
            child_op_types = {c.operator_type for c in self.children.values()}
            return all(op in child_op_types for op in STRUCTURAL_EXPAND_OPS)
        child_op_types = {c.operator_type for c in self.children.values()}
        return all(op in child_op_types for op in STRUCTURAL_EXPAND_OPS)

    # ──────────────────────────────────────────────────────────────────────────
    # Tree mutation
    # ──────────────────────────────────────────────────────────────────────────

    def add_child(
        self,
        configured_step: str,
        new_operation_history: List[str],
        operator_type: Optional[str] = None,
    ) -> "MCTSNode":
        """
        Expand a new child node keyed by the full configured_step string.

        Parameters
        ----------
        configured_step       : full operation string, used as the dict key
                                e.g. "JOIN : [[S0, S1]] columns=[...]"
        new_operation_history : parent history + [configured_step]
        operator_type         : human-readable operator label (metadata only)
        """
        if configured_step in self.children:
            raise ValueError(
                f"Child for configured_step '{configured_step[:60]}...' already exists."
            )
        child = MCTSNode(
            operation_history=new_operation_history,
            parent=self,
            operator_type=operator_type,
        )
        self.children[configured_step] = child
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
            "saturated": self.saturated,
            "reaggregation_needed": self.reaggregation_needed,
        }
        if depth < max_depth:
            # Truncate long keys for readability
            node_dict["children"] = {
                k[:80]: v.to_dict(depth + 1, max_depth)
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
        child_ops = [v.operator_type for v in self.children.values()]
        flags = ""
        if self.saturated:
            flags += " SATURATED"
        if self.reaggregation_needed:
            flags += " REAGG"
        return (
            f"MCTSNode(op={self.operator_type}, "
            f"depth={len(self.operation_history)}, "
            f"visits={self.visits}, "
            f"q={self.q_value:.3f}, "
            f"children={len(self.children)}{flags} {child_ops})"
        )
