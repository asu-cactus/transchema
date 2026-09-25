"""
MCTSNode: the core data structure for MCTS-based schema transformation search.

Each node represents a partial transformation plan (pipeline prefix).
The tree built from MCTSNodes is the cross-iteration memory:
  - visit counts, accumulated rewards, and each child's fixed prior (used as
    a First-Play-Urgency fallback while unvisited) guide UCB1 selection
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
    "COLUMN_TRANSFORM",
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
    "COLUMN_TRANSFORM",
    "NO_MORE_OPERATION",
]

# Structural operator types offered to the LLM as expansion candidates for any
# non-GROUP_BY node (GROUP_BY nodes only ever offer AGGREGATE). No longer used
# to decide when a node is "fully expanded" — see MAX_CHILDREN / is_fully_expanded.
STRUCTURAL_EXPAND_OPS: List[str] = [
    "JOIN", "UNION", "GROUP_BY", "PIVOT", "UNPIVOT",
    "COLUMN_TRANSFORM",
]

# Operator types offered as expansion candidates for an AGGREGATE node.
# GROUP_BY is excluded: grouping again immediately after an aggregation would
# re-group an already-aggregated table, which is never a valid step here, and
# it is what produced the GROUP_BY -> AGGREGATE -> GROUP_BY chains seen in the
# trees. Enforced both in the expand prompt's allowed_operation_list and in
# get_mcts_candidates' operator filter.
POST_AGGREGATE_EXPAND_OPS: List[str] = [
    "JOIN", "UNION", "PIVOT", "UNPIVOT",
    "COLUMN_TRANSFORM",
]


DEFAULT_EXPLORATION_WEIGHT: float = math.sqrt(2)


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
    - UCB1 uses these accumulated stats to balance exploration vs exploitation;
      an unvisited node falls back to its fixed prior (First Play Urgency)
      instead of the classic +inf, so it competes on a bounded, comparable
      score rather than automatically winning.
    - best_script / best_score cache the highest-scoring result seen from this subtree.
    """

    # A node is considered "fully expanded" once it has this many children —
    # applies uniformly to every operator type, including GROUP_BY's AGGREGATE
    # children. mcts_select will then descend past it into its children.
    MAX_CHILDREN: int = 5

    def __init__(
        self,
        operation_history: List[str],
        parent: Optional["MCTSNode"] = None,
        operator_type: Optional[str] = None,
        prior: float = 0.0,
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

        # Fixed prior — the merged LLM+rule score (S_combined) this candidate
        # was ranked at when it was proposed during expansion. Looked up ONCE
        # at creation time, never touched by update()/backpropagate — kept
        # entirely separate from real reward statistics (visits/total_reward
        # are never seeded from it). Used only as ucb1()'s First-Play-Urgency
        # fallback for an unvisited node, in place of +inf. Root has no
        # incoming candidate score, so it stays 0.0 (neutral, unused — root's
        # own children compete on their own priors, not root's).
        self.prior: float = prior

    # ──────────────────────────────────────────────────────────────────────────
    # UCB1 / selection helpers
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def depth(self) -> int:
        """
        Logical depth in the tree; root = 0.
        GROUP_BY + AGGREGATE count as one combined step, so AGGREGATE steps
        are excluded from the count (they share the depth slot with their GROUP_BY).
        """
        return sum(
            1 for step in self.operation_history
            if step.split(":")[0].strip() != "AGGREGATE"
        )

    @property
    def q_value(self) -> float:
        """Average reward (exploitation term)."""
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    def ucb1(self, exploration_weight: float = DEFAULT_EXPLORATION_WEIGHT) -> float:
        """
        UCB1 score used by tree policy, with prior-based First Play Urgency:
        an unvisited node (or one whose parent has no visits yet) returns
        self.prior instead of +inf. prior is the fixed S_combined score this
        candidate was ranked at when proposed (see add_child) — already
        scaled comparably to q_value (both roughly [0,1] here), so it
        competes directly against already-visited siblings on a real,
        bounded score instead of automatically winning. This is what removes
        the old "every sibling must get one visit before any can be
        compared" behavior, without seeding fake visits/reward into the
        node's real statistics.

        For a visited node, this is classic UCB1 — unchanged:
            q_value + exploration_weight * sqrt(log(N_parent) / N_self)
        """
        if self.visits == 0 or self.parent is None or self.parent.visits == 0:
            return self.prior
        return self.q_value + exploration_weight * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

    def best_child(self, exploration_weight: float = DEFAULT_EXPLORATION_WEIGHT) -> "MCTSNode":
        """Return the child with the highest UCB1 score."""
        return max(self.children.values(), key=lambda c: c.ucb1(exploration_weight))

    def is_fully_expanded(self) -> bool:
        """
        Fully expanded once this node has MAX_CHILDREN children (uniform
        across every operator type, including GROUP_BY), or once saturated
        (the LLM/rule engine has no new candidates left to propose).
        """
        return self.saturated or len(self.children) >= MCTSNode.MAX_CHILDREN

    # ──────────────────────────────────────────────────────────────────────────
    # Tree mutation
    # ──────────────────────────────────────────────────────────────────────────

    def add_child(
        self,
        configured_step: str,
        new_operation_history: List[str],
        operator_type: Optional[str] = None,
        prior: float = 0.0,
    ) -> "MCTSNode":
        """
        Expand a new child node keyed by the full configured_step string.

        Parameters
        ----------
        configured_step       : full operation string, used as the dict key
                                e.g. "JOIN : [[S0, S1]] columns=[...]"
        new_operation_history : parent history + [configured_step]
        operator_type         : human-readable operator label (metadata only)
        prior                 : S_combined score this candidate was ranked at when
                                proposed — becomes the child's fixed prior (used as
                                ucb1()'s First-Play-Urgency fallback while unvisited)
        """
        if configured_step in self.children:
            raise ValueError(
                f"Child for configured_step '{configured_step[:60]}...' already exists."
            )
        child = MCTSNode(
            operation_history=new_operation_history,
            parent=self,
            operator_type=operator_type,
            prior=prior,
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
            "prior": round(self.prior, 4),
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

    def best_reward_path(self) -> List["MCTSNode"]:
        """
        Greedily descend by total_reward (raw accumulated sum, visit-independent).
        Each step picks the child with the highest total_reward; terminates at
        a leaf (no children). The leaf's best_script is the final answer because
        any node with total_reward > 0 must have been simulated at least once.
        """
        path = [self]
        node = self
        while node.children:
            node = max(node.children.values(), key=lambda c: c.total_reward)
            path.append(node)
        return path

    def __repr__(self) -> str:
        child_ops = [v.operator_type for v in self.children.values()]
        flags = ""
        if self.saturated:
            flags += " SATURATED"
        return (
            f"MCTSNode(op={self.operator_type}, "
            f"depth={len(self.operation_history)}, "
            f"visits={self.visits}, "
            f"q={self.q_value:.3f}, "
            f"prior={self.prior:.3f}, "
            f"children={len(self.children)}{flags} {child_ops})"
        )
