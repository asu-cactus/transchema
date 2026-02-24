# MCTS + LangGraph Schema Transformation

**Configuration 1: Accuracy-First, Latency/Cost-Insensitive**

---

## 1. MCTS

### States

A state `S` is the **partial operator sequence** applied to the source tables so far:

```
S = operation_history: List[str]
```

Examples:
```
S₀ = []                                                     ← root (nothing applied yet)
S₁ = ["JOIN : [order_id = order_id]"]                       ← after one expansion
S₂ = ["JOIN : [order_id = order_id]", "GROUP_BY/AGGREGATE"] ← after two expansions
```

Each state is stored in an `MCTSNode`. The tree is a DAG of states where each edge is one operator choice.

---

### Actions

At any state, the LLM can choose one of **6 operators**:

| Action | Configuration (extra LLM call?) | Terminal? |
|--------|--------------------------------|-----------|
| `JOIN` | Yes — join columns | No |
| `UNION` | Yes — tables to stack | No |
| `GROUP_BY/AGGREGATE` | Yes — group key + agg function | No |
| `PIVOT` | No | No |
| `UNPIVOT` | No | No |
| `NO_MORE_OPERATION` | No | **Yes** |

`NO_MORE_OPERATION` is the only terminal action. When a node was reached via `NO_MORE_OPERATION`, it is marked `is_terminal=True` and cannot be expanded further.

The tree is keyed by **operator type** (not by configuration string), so each node has at most **6 children**. When the LLM picks the same operator type again in a later iteration, it follows the existing branch rather than forking — this keeps the tree tractable.

---

### The Four MCTS Phases

#### Phase 1 — Selection

**Goal**: find the most promising node in the existing tree to expand next.

Starting from the root, repeatedly descend using **UCB1** until reaching a node that has at least one untried operator type (or is terminal):

```
UCB1(node) = Q(node) + C · √( log(N(parent)) / N(node) )
           = total_reward / visits  +  1.414 · √( log(parent.visits) / visits )
```

- Nodes with `visits = 0` get `UCB1 = ∞` → always explored first (exploration).
- Once all children of a node are visited, UCB1 balances exploitation (`Q`) with exploration (the second term).

**Result**: `selected_node` — the node to expand; `selection_path` — the full path from root to that node (used later in backpropagation).

---

#### Phase 2 — Expansion

**Goal**: add exactly **one new operator** to the selected node.

Two LLM calls are made:
1. `get_next_operator` prompt → LLM suggests which operator to apply next.
2. `join` / `group_by_aggregate` / `union` prompt → LLM configures that operator (if needed).

The result (e.g. `"JOIN : [order_id = order_id]"`) is appended to `operation_history`. A new `MCTSNode` is created as a child of `selected_node` (keyed by operator type) and added to `selection_path`.

If the LLM suggests an operator type already tried at this node, MCTS simply follows that existing branch — no duplicate node is created, but the simulation still runs.

**Result**: `rollout_history = selected_node.operation_history + [configured_op]` — the history that will be handed to simulation.

---

#### Phase 3 — Simulation

**Goal**: from the expanded node's partial history, get a **reward signal** as fast as possible.

Instead of rolling out operator-by-operator (costly, requires multiple LLM calls), simulation goes directly to **code generation**:

1. Pass `rollout_history` to the `python_script` LLM prompt.
2. The LLM generates a **complete Python script** that implements the full transformation — it decides what additional operations are needed beyond the given partial plan.
3. Execute the script with `execute_python()`.
4. If execution fails, feed the error back to the LLM and retry (up to 5 times).

This means one operator in the history = one LLM expansion call + one LLM code-generation call per iteration. No intermediate operator steps.

**Result**: `current_script` and `current_response` ("Success" or error string).

---

#### Phase 4 — Backpropagation

**Goal**: propagate the reward up the tree so all ancestors learn from this simulation.

Compute the reward:
```
reward = calculate_score(ground_truth_df, generated_df)
       = w·score_fd + w·score_key + w·column_mapping_score
```

Walk `selection_path` **from expanded node back to root**, updating each node in-place:
```
node.visits        += 1
node.total_reward  += reward
node.best_score     = max(node.best_score, reward)
```

The best script is also cached on the expanded node. After backpropagation, UCB1 scores across the tree are updated — the next iteration's selection will favour paths that gave higher rewards.

---

## 2. LangGraph

### Nodes

| Node | MCTS Phase | What it does |
|------|-----------|--------------|
| `mcts_select` | Selection | UCB1 walk from root → sets `selected_node` and `selection_path` |
| `next_operator_step` | Expansion | Two LLM calls (ask operator + configure it); adds child to tree; sets `rollout_history` |
| `simulate` | Simulation | LLM generates complete Python pipeline from `rollout_history`; executes with up to 5 retries; sets `current_script`, `current_response` |
| `execute_and_score` | Scoring | Loads output CSV; calls `calculate_score(gt, output)` → `current_score`; updates `best_score` if improved |
| `backpropagate` | Backpropagation | Walks `selection_path`, calls `node.update(reward)` on each; increments `iteration` |
| `extract_best` | Finalisation | Logs tree summary; saves best script to disk; returns |

---

### Edges

```
START
  │
  ▼
[mcts_select]
  │
  ├─ "terminal" (selected node is a NO_MORE_OPERATION leaf) ──────────┐
  │                                                                    │
  └─ "expand"  (selected node has untried operators)                  │
        │                                                              │
        ▼                                                              │
[next_operator_step]                                                   │
        │                                                              │
        └──────────────────────────────────────────────────────────────┤
                                                                       ▼
                                                                 [simulate]
                                                                       │
                                                                       ▼
                                                             [execute_and_score]
                                                                       │
                                                                       ▼
                                                              [backpropagate]
                                                                       │
                                              ┌────────────────────────┴──────────────┐
                                           "iterate"                               "done"
                                        (iteration <                         (iteration >=
                                         max_iterations)                      max_iterations)
                                              │                                    │
                                              ▼                                    ▼
                                        [mcts_select]                      [extract_best]
                                     (MCTS iteration loop)                         │
                                                                                   ▼
                                                                                  END
```

**Conditional edges summary:**

| From | Condition function | Routes |
|------|--------------------|--------|
| `mcts_select` | `is_selected_terminal` | `"terminal"` → `simulate` · `"expand"` → `next_operator_step` |
| `backpropagate` | `check_budget` | `"iterate"` → `mcts_select` · `"done"` → `extract_best` |

All other edges are static (always followed).

---

### Memory

The graph has **two kinds of memory**:

#### Tree-Based Memory (cross-iteration)

The `MCTSNode` tree stored in `MCTSGraphState["root"]` is the primary memory. It persists and grows across all MCTS iterations within a single case run.

Each node stores:

| Field | Type | Role |
|-------|------|------|
| `operation_history` | `List[str]` | The operator sequence that defines this state |
| `visits` | `int` | How many MCTS iterations passed through this node |
| `total_reward` | `float` | Sum of `calculate_score` rewards from all those iterations |
| `best_score` | `float` | Highest single reward seen from this subtree |
| `best_script` | `str` | Python script that achieved `best_score` |
| `children` | `Dict[op_type, MCTSNode]` | Edges to child states (≤ 6 per node) |

This memory directly feeds UCB1: nodes that were visited many times with high rewards get lower exploration bonus, nodes with few visits get higher. The tree encodes **which operator sequences are worth pursuing** across all iterations.