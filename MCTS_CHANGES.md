# MCTS Redesign — Change Log

This document records every change made to the MCTS codebase in this session,
the file it lives in, and the motivation behind it.

---

## 1. Remove `NO_MORE_OPERATION` from Expansion

**Goal:** Expansion should always grow the tree in a structural direction.
Only simulation and critique decide when a plan is complete.

### `prompts/mcts_expand.py`
- Removed `NO_MORE_OPERATION` from the module docstring example.
- Removed the `NO_MORE_OPERATION` format block from the prompt body.
- Replaced the selection-guidance line *"propose NO_MORE_OPERATION if done"*
  with *"always propose at least one structural operator; termination is decided
  later."*

### `Langraph/nodes.py` — `next_operator_step`
- Changed `expand_ops` to filter `NO_MORE_OPERATION` from the allowed list
  passed to the LLM and candidate parser.
- **Fallback (empty/unparseable response):** instead of adding a
  `NO_MORE_OPERATION` child to the tree, the node is marked `saturated` and
  simulation re-runs from the existing prefix. `NO_MORE_OPERATION` is now
  **never added to the tree** by any expansion path.

### `Langraph/nodes.py` — `_find_or_create_path`
- Strips all `NO_MORE_OPERATION` steps from the input history before building
  tree nodes. Simulation plans end with this marker, but it must never
  materialise as a tree node.

---

## 2. Split `GROUP_BY/AGGREGATE` into Separate Operators

**Goal:** Allow the MCTS tree to independently explore different aggregation
configurations under the same group-by key selection. The tree has separate
`GROUP_BY` and `AGGREGATE` nodes; simulation and code-gen still see the old
combined `GROUP_BY/AGGREGATE` string.

### `Langraph/mcts_node.py`
- Added `EXPAND_OPERATOR_TYPES` — the full operator list for the expand layer,
  containing `GROUP_BY` and `AGGREGATE` as separate entries instead of
  `GROUP_BY/AGGREGATE`.

### `hints/hints_static.py`
- Added `GROUPBY_HINT_IDS = [10, 11, 12, 13, 14]` — hints specific to
  choosing group-by columns.
- Added `AGGREGATE_HINT_IDS = [14, 16, 17, 18, 19, 20, 21]` — hints specific
  to choosing aggregation functions.

### `prompts/mcts_expand.py`
- Replaced the `GROUP_BY/AGGREGATE` configuration block with a `GROUP_BY`-only
  block (columns only; aggregation is the next step).
- Updated the imports to include `GROUPBY_HINT_IDS` and `AGGREGATE_HINT_IDS`.
- Added **`get_mcts_expand_aggregate_prompt()`** — a new prompt function called
  when the selected tree node is `GROUP_BY`. It shows the already-chosen
  group-by step and asks for up to k independent `AGGREGATE` candidates, each
  specifying different aggregation functions. Includes all aggregation hints
  (`AGGREGATE_HINT_IDS`).

### `auto_suggest_llm_util.py`
- Imported `get_mcts_expand_aggregate_prompt`.
- Added `"mcts_expand_aggregate"` dispatch block in `get_prompt`, mirroring
  the token-budget logic of `"mcts_expand"`.
- Added `GROUP_BY` and `AGGREGATE` candidate parsing in `get_mcts_candidates`:
  - `GROUP_BY` → configured step `"GROUP_BY : [col1, col2]"`
  - `AGGREGATE` → configured step `"AGGREGATE : [COUNT(col), SUM(col2)]"`

### `Langraph/nodes.py`
- Imported `EXPAND_OPERATOR_TYPES` from `mcts_node`.
- **`_parse_op_type`** — added cases for `"GROUP_BY :"` → `"GROUP_BY"` and
  `"AGGREGATE :"` → `"AGGREGATE"` and `"GROUP_BY/AGGREGATE"` → `"GROUP_BY/AGGREGATE"`.
- **`_merge_groupby_aggregate(history)`** — collapses consecutive
  `GROUP_BY : [cols]` + `AGGREGATE : [funcs]` tree steps into the single
  `GROUP_BY/AGGREGATE : "group_by"=..., "aggregations"=...` string that
  simulation and code-gen understand. Called at the top of `simulate`.
- **`_split_groupby_aggregate(history)`** — the reverse: splits any
  `GROUP_BY/AGGREGATE` step (in either format produced by different prompts)
  back into separate `GROUP_BY` and `AGGREGATE` steps so tree paths stay
  consistent. Applied in `backpropagate` and `mcts_critique` before
  `_find_or_create_path`.
- **`simulate`** — calls `_merge_groupby_aggregate` on `rollout_history` before
  dispatching to simulation helpers so simulation always sees the combined format.
- **`backpropagate`** — calls `_split_groupby_aggregate` on `current_full_history`
  before computing `truncated_sim`, ensuring depths align correctly between the
  (unmerged) tree path and the (merged) simulation output.
- **`mcts_critique`** — calls `_split_groupby_aggregate` on `critique_plan` for
  the same reason before passing to `_find_or_create_path`.
- **`next_operator_step`** — detects `selected_node.operator_type == "GROUP_BY"`:
  - If yes → uses `"mcts_expand_aggregate"` prompt, `expand_ops = ["AGGREGATE"]`.
  - If no → uses `"mcts_expand"` prompt, filters `expand_ops` to uncovered
    structural operator types only.

---

## 3. Expansion Criterion: Operator-Type Coverage

**Goal:** Replace the old fixed `MAX_CHILDREN = 3` slot-filling model with
one where a node is fully expanded only when every distinct structural operator
type has been explored at least once as a child. This ensures breadth before
depth.

### `Langraph/mcts_node.py`
- Added `STRUCTURAL_EXPAND_OPS = ["JOIN", "UNION", "GROUP_BY", "PIVOT", "UNPIVOT"]` —
  the set of types required for a standard node to be considered fully expanded.
- Added `POST_AGGREGATE_EXPAND_OPS = ["JOIN", "UNION", "PIVOT", "UNPIVOT"]` —
  same but for `AGGREGATE` nodes. `GROUP_BY` is intentionally excluded: the
  system must not *mandate* a GROUP_BY child after every AGGREGATE (which would
  cause unbounded GROUP_BY → AGGREGATE → GROUP_BY → ... chains). The LLM may
  still *propose* GROUP_BY after AGGREGATE freely.
- **`is_fully_expanded()`** — three-way logic:
  1. `GROUP_BY` node: fully expanded as soon as any `AGGREGATE` child exists
     (one or more variants). UCB1 can descend immediately; re-expansion is
     driven by `reaggregation_needed`.
  2. `AGGREGATE` node: fully expanded when all types in `POST_AGGREGATE_EXPAND_OPS`
     are covered as children.
  3. All other nodes: fully expanded when all types in `STRUCTURAL_EXPAND_OPS`
     are covered as children, or when `saturated`.

### `Langraph/nodes.py` — `next_operator_step`
- `expand_ops` for standard expansion now computes **uncovered types only**:
  ```python
  covered = {c.operator_type for c in selected_node.children.values()}
  expand_ops = [op for op in STRUCTURAL_EXPAND_OPS if op not in covered]
  ```
  The LLM is asked only for operator types not yet in the tree, making each
  expansion call additive rather than redundant.
- `explored_steps` — a list of existing children's configured step strings is
  collected and passed to `get_prompt` so the expansion prompt can show the LLM
  what has already been tried at this position.

---

## 4. Reaggregation: Adaptive GROUP_BY Re-expansion

**Goal:** If a GROUP_BY node proves promising (good reward from its AGGREGATE
children), allow more AGGREGATE variants to be explored beyond the initial
batch — up to a cap of 9.

### `Langraph/mcts_node.py`
- Added `AGGREGATE_MAX_CHILDREN = 9`.
- Added `self.reaggregation_needed: bool = False` on every `MCTSNode`.
  Set by `backpropagate` when an AGGREGATE subtree under a GROUP_BY node scores
  above the threshold and the node still has room for more children.
- `to_dict()` and `__repr__` updated to expose `reaggregation_needed`.

### `Langraph/nodes.py`
- Added `_REAGGREGATION_REWARD_THRESHOLD = 0.5`.
- **`mcts_select`** — inside the descent loop, checks if the current node is a
  `GROUP_BY` with `reaggregation_needed=True` and fewer than
  `AGGREGATE_MAX_CHILDREN` children. If so, clears the flag and breaks out of
  the loop, stopping here for re-expansion rather than descending to existing
  children.
- **`backpropagate`** — in both Pass 1 (simulate path) and Pass 2 (critique
  path), after `node.update(reward)`, sets `node.reaggregation_needed = True`
  on any `GROUP_BY` node where `reward >= _REAGGREGATION_REWARD_THRESHOLD`
  and there is still room for more AGGREGATE children.

---

## 5. Explored-Steps Context in Expansion Prompts

**Goal:** Tell the LLM what has already been tried at a given position so it
proposes genuinely new candidates rather than re-proposing explored configs.

### `prompts/mcts_expand.py`
- `get_mcts_expand_prompt` — added `explored_steps=None` parameter. When
  non-empty, injects an "ALREADY EXPLORED AT THIS POSITION" section listing
  explored configs and the remaining uncovered operator types.
- `get_mcts_expand_aggregate_prompt` — added `explored_steps=None` parameter.
  When non-empty, injects an "ALREADY EXPLORED AGGREGATIONS" section listing
  tried aggregation configs.

### `auto_suggest_llm_util.py`
- Added `explored_steps=None` to `get_prompt`. Forwarded to both
  `get_mcts_expand_prompt` and `get_mcts_expand_aggregate_prompt` in their
  respective dispatch blocks.

### `Langraph/nodes.py` — `next_operator_step`
- `explored_steps = list(selected_node.children.keys())` is computed before the
  LLM call and passed through to `get_prompt`.

---

## 6. RAG Pipeline — Flexible Prefix Matching

**Goal:** Allow one MCTS `UNION` operation to match one or more consecutive
`concat`/`union` steps in a RAG pipeline (because pandas `pd.concat` is called
once per pair, while MCTS UNION stacks all tables in one call). Also handle the
split `GROUP_BY` + `AGGREGATE` nodes matching the old combined `GROUP_BY/AGGREGATE`
step in stored RAG pipelines.

### `rag_pipeline/local_rag_db.py`
- **`_OP_TO_BIN`** — added:
  - `"GROUP_BY" → "groupby"` (new split expand operator)
  - `"AGGREGATE" → "aggregate"` (new split expand operator)
- **`_flexible_prefix_match(current_abstract, rag_abstract)`** — new function
  replacing the old `abstract[:depth] == current_abstract` strict equality check.
  Two flex rules:
  - **Rule 1 — Union collapse:** one MCTS `"union"` advances the RAG cursor
    past one *or more* consecutive `"union"` bins.
  - **Rule 2 — GroupBy merge:** MCTS `("groupby", "aggregate")` pair matches
    a single RAG `"groupby"` step (the old unsplit format still stored in the DB).
  Returns the index of the next RAG step after the matched prefix, or `None`
  on mismatch.
- **`get_rag_hints`** — refactored to use `_flexible_prefix_match`. `matched`
  is now a list of `(row, next_idx)` tuples where `next_idx` is the exact
  position in the RAG pipeline's step list after the matched prefix. The
  `[done]` / `<<<< NEXT` annotations in the hint text use `next_idx` instead
  of a fixed depth, so they correctly point to the right next step even when
  union steps were collapsed.

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `Langraph/mcts_node.py` | New constants, `reaggregation_needed` flag, new `is_fully_expanded` logic |
| `Langraph/nodes.py` | `_split/merge_groupby_aggregate`, `_parse_op_type`, `_find_or_create_path`, `mcts_select`, `next_operator_step`, `simulate`, `backpropagate`, `mcts_critique` |
| `prompts/mcts_expand.py` | GROUP_BY-only expand, new `get_mcts_expand_aggregate_prompt`, `explored_steps` param, NO_MORE_OPERATION removed |
| `auto_suggest_llm_util.py` | `mcts_expand_aggregate` dispatch, GROUP_BY/AGGREGATE candidate parsing, `explored_steps` param |
| `hints/hints_static.py` | `GROUPBY_HINT_IDS`, `AGGREGATE_HINT_IDS` |
| `rag_pipeline/local_rag_db.py` | `_OP_TO_BIN` additions, `_flexible_prefix_match`, `get_rag_hints` refactor |
