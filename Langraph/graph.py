"""
build_mcts_graph: constructs and compiles the LangGraph StateGraph for MCTS.

Graph topology
--------------

  START
    │
    ▼
  [mcts_select]  ── UCB1 walk → selected leaf
    │
    ├── (terminal) ────────────────────────────────┐
    │   re-simulate an already-expanded leaf        │
    │                                               │
    └── (expand)                                    │
          │                                         │
          ▼                                         │
  [next_operator_step]                              │
    one operator added to tree                      │
          │                                         │
          └─────────────────────────────────────────┤
                                                    ▼
                                              [simulate]
                                    LLM completes full pipeline + code
                                                    │
                                                    ▼
                                          [execute_and_score]
                                        calculate_score → reward
                                                    │
                              score<1.0 + "simulate" mode?
                                   yes ──► [mcts_critique]
                                   no  ──────────┐
                                                 │
                                                 ▼
                                            [backpropagate]
                                       update visits + rewards
                                                    │
                                    ┌───────────────┴───────────────┐
                                 (iterate)                        (done)
                                    │                               │
                                    ▼                               ▼
                              [mcts_select]                  [extract_best]
                          (MCTS iteration loop)                     │
                                                                    ▼
                                                                   END
"""

import os
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from langgraph.graph import END, START, StateGraph

from nodes import (
    backpropagate,
    check_budget,
    execute_and_score,
    extract_best,
    is_selected_terminal,
    mcts_critique,
    mcts_select,
    next_operator_step,
    should_critique,
    simulate,
)
from state import MCTSGraphState


def build_mcts_graph():
    """
    Build and compile the MCTS LangGraph.

    Returns
    -------
    CompiledGraph
        A compiled LangGraph that accepts MCTSGraphState and runs MCTS.
    """
    graph = StateGraph(MCTSGraphState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("mcts_select", mcts_select)
    graph.add_node("next_operator_step", next_operator_step)
    graph.add_node("simulate", simulate)
    graph.add_node("execute_and_score", execute_and_score)
    graph.add_node("mcts_critique", mcts_critique)
    graph.add_node("backpropagate", backpropagate)
    graph.add_node("extract_best", extract_best)

    # ── Entry point ───────────────────────────────────────────────────────────
    graph.add_edge(START, "mcts_select")

    # ── After mcts_select: expand or re-simulate a terminal node ──────────────
    graph.add_conditional_edges(
        "mcts_select",
        is_selected_terminal,
        {
            "terminal": "simulate",          # re-simulate existing terminal leaf
            "expand": "next_operator_step",  # expand one new operator
        },
    )

    # ── After expansion: always go straight to simulation ─────────────────────
    # No rollout loop — simulate() completes the pipeline from the expanded history
    graph.add_edge("next_operator_step", "simulate")

    # ── Simulation pipeline: score → optional critique → backpropagate ────────
    graph.add_edge("simulate", "execute_and_score")
    graph.add_conditional_edges(
        "execute_and_score",
        should_critique,
        {
            "critique": "mcts_critique",
            "backpropagate": "backpropagate",
        },
    )
    graph.add_edge("mcts_critique", "backpropagate")

    # ── MCTS iteration loop: continue or finish ────────────────────────────────
    graph.add_conditional_edges(
        "backpropagate",
        check_budget,
        {
            "iterate": "mcts_select",   # more iterations remaining
            "done": "extract_best",     # budget exhausted
        },
    )

    # ── Terminal edge ─────────────────────────────────────────────────────────
    graph.add_edge("extract_best", END)

    return graph.compile()
