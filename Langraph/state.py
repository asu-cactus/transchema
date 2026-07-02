"""
MCTSGraphState: the LangGraph state TypedDict for the MCTS search graph.

Key insight: `root` is a Python object reference to an MCTSNode.
The tree is mutated in-place during execution — visit counts, rewards,
and new children are added directly to the node objects without
needing to update the `root` key in the state dict on every step.
"""

from typing import Any, List
from typing_extensions import TypedDict


class MCTSGraphState(TypedDict):
    """
    Full state flowing through the MCTS LangGraph.

    Sections
    --------
    Problem config       — read-only throughout the search
    Tree-based memory    — the MCTSNode tree, mutated in-place
    Iteration control    — which MCTS iteration we are on
    Selection phase      — which path was selected by UCB1
    Rollout phase        — current simulation state
    Simulation results   — output of the latest code gen + scoring
    Best result          — best found across all iterations
    Logging              — human-readable trace for debugging
    """

    # ── Problem config (read-only) ────────────────────────────────────────────
    config: Any                      # Config dataclass from methods/multi_step.py
    main_folder: str                 # e.g. "autopipeline-benchmarks/github-pipelines"
    ground_truth_location: str       # path to target.csv
    target_file_location: str        # path where generated CSV is written
    validation_mode: str             # "hard_match" or "autopipeline"
    reward_mode: str                 # "score" | "det_score_value" | "validation" | "partial"
    experiment_name: str             # label for saved scripts
    case_id: str                     # e.g. "2_5" for length2_5

    # Prompt extras not in Config (default to 0/[] when not provided by args)
    join_flag: int
    join_hints_truncate: List[float]
    aggregate_flag: int
    aggregate_hints_truncate: List[float]
    few_shot: int

    # ── Tree-based memory ─────────────────────────────────────────────────────
    # The MCTS tree IS the cross-iteration memory.
    # This reference is stable; child nodes and stats are added in-place.
    root: Any                        # MCTSNode — root of the search tree

    # ── MCTS iteration control ────────────────────────────────────────────────
    iteration: int                   # current iteration index (0-based, incremented by backpropagate)
    max_iterations: int              # hard budget cap (safety limit; ignored when cost_budget > 0)
    max_depth: int                   # hard cap on tree depth; nodes at this depth are forced leaves
    early_stopping: int              # stop if best_score doesn't improve for this many iters; 0 = disabled
    cost_budget: float               # max USD to spend per case; 0.0 = disabled (use iteration mode)
    cost_budget_exhausted: bool      # True once LLMClient blocked a request due to budget; triggers immediate stop
    terminal_found: bool             # True once a NO_MORE_OPERATION node has been simulated
    validation_passed: bool          # True once any iteration validates against ground truth

    # ── Selection phase ───────────────────────────────────────────────────────
    # Set by mcts_select; consumed by next_operator_step + backpropagate.
    selection_path: List[Any]        # [MCTSNode, ...] from root to the selected leaf
    selected_node: Any               # MCTSNode at the end of selection_path

    # ── Rollout / expansion phase ─────────────────────────────────────────────
    # Tracks the current simulation (one per MCTS iteration).
    rollout_history: List[str]       # operation_history being built this simulation
    rollout_step: int                # depth within this simulation
    in_rollout: bool                 # False = expansion step; True = pure rollout
    current_operator: str            # last operator type returned by LLM

    # ── Simulation results ────────────────────────────────────────────────────
    current_script: str              # Python code generated this iteration
    current_score: float             # calculate_score reward for this iteration
    current_response: str            # "Success" or error string from execute_python
    current_full_history: List[str]  # complete pipeline parsed from $PLAN$ block (may be [] if unparseable)

    # ── Best result across all iterations ─────────────────────────────────────
    best_script: str
    best_score: float
    best_operation_history: List[str]
    no_improvement_count: int        # consecutive iterations without best_score improvement
    latest_script: str               # most recently executed script regardless of score

    # ── Simulation mode ───────────────────────────────────────────────────────
    simulation_mode: str                 # "pipeline" (default) | "operator"
    intermediate_materialization: bool   # True = materialize + score at each operator step (operator mode only)

    # ── LLM Judge ────────────────────────────────────────────────────────────
    llm_judge: str                        # "none" | "det_score" | "llm" | "llm_score" | "llm_score_hybrid"
    judge_verdict: bool                   # cached judge result for the current iteration

    # ── Critique phase ────────────────────────────────────────────────────────
    critique_attempted: bool             # True once critique has run this MCTS iteration
    pre_critique_score: float            # simulation score before critique altered the pipeline
    critique_selection_path: List[Any]   # [MCTSNode, ...] for the corrected plan generated by critique
    critique_score: float                # score of the critique's corrected output

    # ── Stopping criteria ─────────────────────────────────────────────────────
    # When True, score-based early stopping is suppressed for "score" and
    # "det_score_value" reward modes — the search runs to its full budget and
    # the best-scoring script is chosen at the end.  Used for failed-case reruns.
    no_score_threshold: bool

    # ── RAG support ───────────────────────────────────────────────────────────
    # Path to the per-case SQLite DB built from similar retrieved cases.
    # Empty string means RAG is disabled for this run.
    local_rag_db_path: str

    # ── GT scoring cache ──────────────────────────────────────────────────────
    # Path to a JSON file with pre-computed GT-side FDs and self-column-map count.
    # Written once per case in mcts_search.py; consumed by execute_and_score to
    # skip redundant FD mining on the (static) ground-truth table each iteration.
    # Empty string means no cache available; scoring falls back to full recomputation.
    gt_score_cache_path: str

    # ── Debug log ─────────────────────────────────────────────────────────────
    log_messages: List[str]
