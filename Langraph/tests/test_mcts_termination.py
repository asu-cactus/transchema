import unittest
from unittest.mock import patch
import os
import sys

# Match Langraph's module import style (sibling imports like "from mcts_node import ...")
_HERE = os.path.dirname(os.path.abspath(__file__))
_LANGRAPH_DIR = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_LANGRAPH_DIR)
for _p in (_LANGRAPH_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mcts_node import MCTSNode
from nodes import (
    backpropagate,
    check_budget,
    execute_and_score,
    mcts_critique,
    should_critique,
)


class _DummyLogger:
    def info(self, *_args, **_kwargs):
        return None

    def warning(self, *_args, **_kwargs):
        return None


class _DummyConfig:
    def __init__(self, mcts_critique_mode="none"):
        self.logger = _DummyLogger()
        self.mcts_critique_mode = mcts_critique_mode


def _build_state(**overrides):
    root = MCTSNode(operation_history=[], parent=None, operator_type=None)
    state = {
        "config": _DummyConfig(),
        "main_folder": "",
        "ground_truth_location": "ground_truth.csv",
        "target_file_location": "generated.csv",
        "validation_mode": "hard_match",
        "experiment_name": "exp",
        "case_id": "1_1",
        "join_flag": 0,
        "join_hints_truncate": [],
        "aggregate_flag": 0,
        "aggregate_hints_truncate": [],
        "few_shot": 0,
        "root": root,
        "iteration": 0,
        "max_iterations": 10,
        "terminal_found": False,
        "validation_passed": False,
        "selection_path": [root],
        "selected_node": root,
        "rollout_history": ["OP_A"],
        "rollout_step": 1,
        "in_rollout": True,
        "current_operator": "OP_A",
        "current_script": "print('ok')",
        "current_score": 0.0,
        "current_response": "Success",
        "current_full_history": ["OP_A", "NO_MORE_OPERATION"],
        "best_script": "",
        "best_score": 0.0,
        "best_operation_history": [],
        "no_improvement_count": 0,
        "critique_attempted": False,
        "log_messages": [],
    }
    state.update(overrides)
    return state


class TestMCTSTermination(unittest.TestCase):
    def test_check_budget_done_when_validation_passed(self):
        state = _build_state(validation_passed=True)
        self.assertEqual(check_budget(state), "done")

    def test_check_budget_done_on_five_no_improvement(self):
        state = _build_state(no_improvement_count=5)
        self.assertEqual(check_budget(state), "done")

    def test_check_budget_done_on_iteration_cap(self):
        state = _build_state(iteration=10, max_iterations=10)
        self.assertEqual(check_budget(state), "done")

    def test_check_budget_does_not_stop_on_terminal_flag_only(self):
        state = _build_state(terminal_found=True)
        self.assertEqual(check_budget(state), "iterate")

    def test_check_budget_does_not_stop_on_high_best_score_only(self):
        state = _build_state(best_score=0.99)
        self.assertEqual(check_budget(state), "iterate")

    @patch("nodes._score_and_validate_output", return_value=(0.42, True))
    def test_validation_true_exits_same_iteration_path(self, _mock_eval):
        state = _build_state(config=_DummyConfig(mcts_critique_mode="simulate"))

        score_updates = execute_and_score(state)
        state_after_score = {**state, **score_updates}
        self.assertTrue(state_after_score["validation_passed"])
        self.assertEqual(should_critique(state_after_score), "backpropagate")

        backprop_updates = backpropagate(state_after_score)
        state_after_backprop = {**state_after_score, **backprop_updates}
        self.assertEqual(state_after_backprop["iteration"], 1)
        self.assertEqual(check_budget(state_after_backprop), "done")

    @patch("nodes._score_and_validate_output", return_value=(1.0, True))
    def test_validation_true_promotes_current_script_even_on_tie(self, _mock_eval):
        state = _build_state(
            best_score=1.0,
            best_script="old_script()",
            best_operation_history=["OLD_PLAN"],
            current_script="new_valid_script()",
            current_full_history=["NEW_PLAN", "NO_MORE_OPERATION"],
        )

        updates = execute_and_score(state)
        self.assertTrue(updates["validation_passed"])
        self.assertEqual(updates["best_script"], "new_valid_script()")
        self.assertEqual(updates["best_operation_history"], ["NEW_PLAN", "NO_MORE_OPERATION"])

    @patch(
        "nodes._run_critique_llm",
        return_value=("crit_valid()", 0.8, "Success", True, [], None, 0.9, "0.9", "raw response"),
    )
    def test_critique_validation_true_promotes_script_even_on_lower_score(self, _mock_crit):
        state = _build_state(
            best_score=1.0,
            best_script="old_script()",
            best_operation_history=["OLD_PLAN"],
            current_script="current_script()",
            current_full_history=["CRIT_PLAN", "NO_MORE_OPERATION"],
        )

        updates = mcts_critique(state)
        self.assertTrue(updates["validation_passed"])
        self.assertEqual(updates["best_script"], "crit_valid()")
        self.assertEqual(updates["best_operation_history"], ["CRIT_PLAN", "NO_MORE_OPERATION"])


if __name__ == "__main__":
    unittest.main()
