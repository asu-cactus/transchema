"""
eval_run8_training.py
======================
Evaluate the run8 L1 training MCTS experiment by running extracted scripts on
TEST data and measuring autopipeline correctness.

Two methods compared:
  Method A (Best Score):  Script that achieved the highest det_score_value on
                          training data during MCTS search.
  Method B (Greedy TR):   Script at the leaf of the greedy total_reward path.
  Method B' (BOP):        Script at the best-on-path node of the greedy TR path.

For each method the script's training_N.csv paths are swapped to test_N.csv,
the script is executed, and the output is validated with compare_tables_matching.

Usage
-----
  python eval_run8_training.py [--dry_run] [--cases 0 5 17] [--verbose]
"""

import sys
import os
import re
import ast
import csv
import io
import subprocess
import tempfile
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, List
from contextlib import redirect_stdout, redirect_stderr

# ── Project imports ──────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from validation.hard_match import compare_tables_matching
import pandas as pd


# ===========================================================================
# Augmented tree node
# ===========================================================================

@dataclass
class ReconNode:
    op: str
    cfg: str
    depth: int
    visits: int = 0
    total_reward: float = 0.0
    best: float = 0.0
    best_iter: int = -1         # which iteration set this node's best score
    best_is_critique: bool = False  # True if critique script set the best
    children: dict = field(default_factory=dict)
    parent: Optional["ReconNode"] = field(default=None, repr=False)

    @property
    def q(self) -> float:
        return self.total_reward / self.visits if self.visits > 0 else 0.0


# ===========================================================================
# Tree helpers (mirrors replay_mcts_from_log.py)
# ===========================================================================

def _child_key(cfg: str) -> str:
    return cfg[:80]


def _lookup_child(parent: ReconNode, cfg: str) -> Optional[ReconNode]:
    if cfg in parent.children:
        return parent.children[cfg]
    key80 = _child_key(cfg)
    for existing_key, child in list(parent.children.items()):
        if _child_key(existing_key) == key80:
            if len(cfg) > len(existing_key):
                parent.children[cfg] = parent.children.pop(existing_key)
                child.cfg = cfg
            return child
    return None


def _get_or_create_child(parent: ReconNode, cfg: str) -> ReconNode:
    child = _lookup_child(parent, cfg)
    if child is None:
        op_type = cfg.split(":")[0].strip().split(" ")[0]
        child = ReconNode(op=op_type, cfg=cfg, depth=parent.depth + 1)
        child.parent = parent
        parent.children[cfg] = child
    return child


def find_or_create_path(root: ReconNode, ops: list) -> list:
    path = [root]
    node = root
    for op in ops:
        node = _get_or_create_child(node, op)
        path.append(node)
    return path


# ===========================================================================
# GROUP_BY/AGGREGATE splitter (mirrors nodes.py)
# ===========================================================================

_GBA_RE1_GB  = re.compile(r'"group_by"\s*=\s*(\[.*?\])')
_GBA_RE1_AGG = re.compile(r'"aggregations"\s*=\s*(\[.*\])\s*$', re.DOTALL)
_GBA_RE2_GB  = re.compile(r'group_by=(\[.*?\])')
_GBA_RE2_AGG = re.compile(r'aggregations=(\[.*\])\s*$', re.DOTALL)


def _split_gba(history: list) -> list:
    result = []
    for step in history:
        if "GROUP_BY/AGGREGATE" not in step:
            result.append(step)
            continue
        after = step.split(":", 1)[1].strip() if ":" in step else step
        m_gb  = _GBA_RE1_GB.search(after)
        m_agg = _GBA_RE1_AGG.search(after)
        if m_gb and m_agg:
            result.append(f"GROUP_BY : {m_gb.group(1)}")
            result.append(f"AGGREGATE : {m_agg.group(1).strip()}")
            continue
        m_gb  = _GBA_RE2_GB.search(after)
        m_agg = _GBA_RE2_AGG.search(after)
        if m_gb and m_agg:
            result.append(f"GROUP_BY : {m_gb.group(1)}")
            result.append(f"AGGREGATE : {m_agg.group(1).strip()}")
            continue
        result.append(step)
    return result


# ===========================================================================
# Log-parsing regexes
# ===========================================================================

RE_SELECT     = re.compile(r'\[MCTS Select\] Iter (\d+):')
RE_EXPAND_ADD = re.compile(r'\[expand\] Iter (\d+): added (?:child|hints_v3 \w+) (?:op=\w+ )?cfg=(.+?) \((?:tree now|$)')
RE_SIMULATE   = re.compile(r'\[simulate\] Iter (\d+): mode=\w+, history=(\[.*\])')
RE_PIPELINE   = re.compile(r'\[simulate/pipeline\] Parsed complete plan: (\[.*\])')
RE_SCORE      = re.compile(r'\[execute_and_score\] Iter (\d+): reward=([\d.]+).*history=(\[.*\])')
RE_CRIT_PLAN  = re.compile(r'\[_run_critique_llm\] Parsed critique plan: (\[.*\])')
RE_CRIT_SCORE = re.compile(r'\[mcts_critique\] Iter (\d+): score [\d.]+ → ([\d.]+)')
RE_CRIT_PATH  = re.compile(r'\[mcts_critique\] Critique path created: (\d+) nodes \(plan_len=\d+ → capped at depth=(\d+)\)')
RE_BP_DIVERGE = re.compile(r'\[backpropagate\] Iter (\d+): sim path diverged.*giving (\d+) selection-only nodes')
RE_BP_DONE    = re.compile(r'\[backpropagate\] Iter (\d+) done\. pre_critique_reward=([\d.]+), critique_reward=([\d.]+), root\.visits=(\d+)')
RE_QUERY_TYPE = re.compile(r'INFO - Query of Type : MCTS (\w+)')
RE_RESULT_RCV = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Result Recieved :')
RE_COST_LINE  = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - INFO - Cost of the query')
RE_CODE_OPEN  = re.compile(r'^```[Pp]ython\s*$')
RE_CODE_CLOSE = re.compile(r'^```\s*$')


def _parse_list(s: str) -> list:
    try:
        return ast.literal_eval(s)
    except Exception:
        return []


def _extract_last_code_block(lines: List[str]) -> Optional[str]:
    """Return the content of the LAST ```python...``` block in lines."""
    blocks = []
    in_block = False
    block_buf: List[str] = []
    for line in lines:
        stripped = line.rstrip()
        if RE_CODE_OPEN.match(stripped):
            in_block = True
            block_buf = []
        elif RE_CODE_CLOSE.match(stripped) and in_block:
            in_block = False
            content = "\n".join(block_buf).strip()
            if content and "<corrected code here>" not in content:
                blocks.append(content)
        elif in_block:
            block_buf.append(line)
    return blocks[-1] if blocks else None


# ===========================================================================
# Core parser: reconstructs tree + extracts scripts per iteration
# ===========================================================================

def _reset_cur() -> dict:
    return {
        "iter":            -1,
        "rollout_history": None,
        "llm_plan":        None,
        "pre_score":       0.0,
        "critique_plan":   None,
        "critique_cap":    0,
        "critique_score":  0.0,
        "diverged":        False,
        "n_sel_only":      0,
        "has_critique":    False,
        "expand_children": [],
    }


def parse_log_with_scripts(
    filepath: Path,
) -> Tuple[Optional[ReconNode], Dict[int, dict], str, float, int]:
    """
    Parse one MCTS log file.

    Returns
    -------
    (root, iter_scripts, global_best_script, global_best_score, total_iters)

    iter_scripts : {iter_num: {"sim": str|None, "critique": str|None}}
    global_best_script : Python script with highest training det_score_value
    global_best_score  : the corresponding score
    total_iters : number of completed iterations
    """
    try:
        text = filepath.read_text(errors="replace")
    except Exception:
        return None, {}, "", 0.0, 0

    lines = text.splitlines()
    root = ReconNode(op="ROOT", cfg="ROOT", depth=0)

    cur = _reset_cur()
    iter_scripts: Dict[int, dict] = {}
    global_best_score = 0.0
    global_best_script = ""

    # LLM-response tracking
    current_query_type: Optional[str] = None
    in_llm_response = False
    response_lines: List[str] = []

    total_iters = 0

    for line in lines:
        # ── Track which type of LLM call is happening ─────────────────────
        m = RE_QUERY_TYPE.search(line)
        if m:
            current_query_type = m.group(1)   # "Expand", "Simulate", "Critique", …
            in_llm_response = False
            response_lines = []

        # ── Start of LLM response ─────────────────────────────────────────
        elif RE_RESULT_RCV.search(line):
            in_llm_response = True
            response_lines = [line]

        # ── End of LLM response ───────────────────────────────────────────
        elif RE_COST_LINE.search(line) and in_llm_response:
            in_llm_response = False
            code = _extract_last_code_block(response_lines)
            if code:
                it = cur["iter"]
                if it >= 0:
                    if it not in iter_scripts:
                        iter_scripts[it] = {"sim": None, "critique": None}
                    if current_query_type == "Simulate":
                        iter_scripts[it]["sim"] = code
                    elif current_query_type == "Critique":
                        iter_scripts[it]["critique"] = code
            response_lines = []

        # ── Accumulate response lines ──────────────────────────────────────
        elif in_llm_response:
            response_lines.append(line)

        # ── Select ────────────────────────────────────────────────────────
        m = RE_SELECT.search(line)
        if m:
            cur["iter"] = int(m.group(1))
            cur["expand_children"] = []

        # ── Expand children ────────────────────────────────────────────────
        m = RE_EXPAND_ADD.search(line)
        if m and cur["iter"] >= 0 and int(m.group(1)) == cur["iter"]:
            cur["expand_children"].append(m.group(2).strip())

        # ── Simulate history ───────────────────────────────────────────────
        m = RE_SIMULATE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["rollout_history"] = _split_gba(_parse_list(m.group(2)))
            rollout = cur["rollout_history"]
            if rollout:
                parent_node = find_or_create_path(root, rollout[:-1])[-1]
                for cfg_prefix in cur["expand_children"]:
                    _get_or_create_child(parent_node, cfg_prefix)

        # ── LLM plan ──────────────────────────────────────────────────────
        m = RE_PIPELINE.search(line)
        if m:
            cur["llm_plan"] = _split_gba(_parse_list(m.group(1)))

        # ── Score ──────────────────────────────────────────────────────────
        m = RE_SCORE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["pre_score"] = float(m.group(2))
            if cur["rollout_history"] is None:
                cur["rollout_history"] = _split_gba(_parse_list(m.group(3)))

        # ── Critique plan ──────────────────────────────────────────────────
        m = RE_CRIT_PLAN.search(line)
        if m:
            cur["critique_plan"] = _split_gba(_parse_list(m.group(1)))

        # ── Critique score ─────────────────────────────────────────────────
        m = RE_CRIT_SCORE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["critique_score"] = float(m.group(2))

        # ── Critique path info ─────────────────────────────────────────────
        m = RE_CRIT_PATH.search(line)
        if m:
            cur["has_critique"] = True
            cur["critique_cap"] = int(m.group(2))

        # ── Backprop diverge ───────────────────────────────────────────────
        m = RE_BP_DIVERGE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            cur["diverged"] = True
            cur["n_sel_only"] = int(m.group(2))

        # ── Backprop done — apply all updates ─────────────────────────────
        m = RE_BP_DONE.search(line)
        if m and int(m.group(1)) == cur["iter"]:
            it = cur["iter"]
            pre_score = cur["pre_score"]
            crit_score = cur["critique_score"]

            # Update global best (mirrors execute_and_score + mcts_critique logic)
            it_sc = iter_scripts.get(it, {})
            sim_sc  = it_sc.get("sim") or ""
            crit_sc = it_sc.get("critique") or ""
            if pre_score > global_best_score and sim_sc:
                global_best_score = pre_score
                global_best_script = sim_sc
            if crit_score > global_best_score and crit_sc:
                global_best_score = crit_score
                global_best_script = crit_sc

            _apply_backprop(root, cur)
            total_iters = it + 1
            cur = _reset_cur()

    return root, iter_scripts, global_best_script, global_best_score, total_iters


def _apply_backprop(root: ReconNode, cur: dict) -> None:
    """Replay one iteration's backpropagation, tracking best_iter per node."""
    rollout    = cur["rollout_history"] or []
    llm_plan   = cur["llm_plan"] or rollout
    pre_score  = cur["pre_score"]
    crit_plan  = cur["critique_plan"] or []
    crit_cap   = cur["critique_cap"]
    crit_score = cur["critique_score"]
    diverged   = cur["diverged"]
    n_sel_only = cur["n_sel_only"]
    has_crit   = cur["has_critique"]
    it         = cur["iter"]

    expanded_depth = len(rollout)

    if diverged and llm_plan and expanded_depth > 0:
        sim_path = find_or_create_path(root, llm_plan[:expanded_depth])
    else:
        sim_path = find_or_create_path(root, rollout)

    # Pass 1: sim path
    for node in sim_path:
        node.visits += 1
        node.total_reward += pre_score
        if pre_score > node.best:
            node.best = pre_score
            node.best_iter = it
            node.best_is_critique = False

    # Virtual visits for selection-only nodes
    if diverged and n_sel_only > 0:
        selection_path = find_or_create_path(root, rollout)
        sim_ids = {id(n) for n in sim_path}
        sel_only = [n for n in selection_path if id(n) not in sim_ids]
        for node in sel_only[:n_sel_only]:
            node.visits += 1

    # Pass 2: critique path
    if has_crit and crit_plan and crit_cap > 0:
        crit_path = find_or_create_path(root, crit_plan[:crit_cap])
        for node in crit_path:
            node.visits += 1
            node.total_reward += crit_score
            if crit_score > node.best:
                node.best = crit_score
                node.best_iter = it
                node.best_is_critique = True


# ===========================================================================
# Greedy path helpers
# ===========================================================================

def greedy_tr_path(root: ReconNode) -> List[ReconNode]:
    """Follow the greedy total_reward path from root to leaf."""
    path = [root]
    node = root
    while node.children:
        node = max(node.children.values(), key=lambda c: (c.total_reward, c.visits))
        path.append(node)
    return path


def best_on_path(path: List[ReconNode]) -> ReconNode:
    """Return the node with the highest best score on the path."""
    return max(path, key=lambda n: (n.best, n.visits))


def get_node_script(node: ReconNode, iter_scripts: Dict[int, dict]) -> Optional[str]:
    """Return the Python script that set node.best (sim or critique)."""
    if node.best_iter < 0:
        return None
    it_sc = iter_scripts.get(node.best_iter, {})
    if node.best_is_critique:
        return it_sc.get("critique")
    else:
        return it_sc.get("sim")


# ===========================================================================
# Path substitution
# ===========================================================================

_TRAIN_RE = re.compile(r'(?<=/|")training_(\d+\.csv)')


def swap_training_to_test(script: str) -> str:
    """Replace /training_N.csv → /test_N.csv in file path strings."""
    return re.sub(r'(?<=[/"])training_(\d+\.csv)', r'test_\1', script)


# ===========================================================================
# Script execution and validation
# ===========================================================================

SCRIPT_TIMEOUT = 90  # seconds


def run_script(script: str, work_dir: Path) -> Tuple[bool, str]:
    """
    Write script to a temp file and run it from work_dir.
    Returns (success, error_message).
    """
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="eval_run8_")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            f.write(script)
        result = subprocess.run(
            [sys.executable, tmp_path],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=SCRIPT_TIMEOUT,
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout)[:400]
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)[:200]
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def validate_output(case_num: int, work_dir: Path, length: int = 1) -> Tuple[bool, float]:
    """
    Load target_multisource_mcts.csv (output) and target.csv (ground truth),
    run compare_tables_matching, return (is_correct, similarity).
    """
    case_dir = work_dir / f"autopipeline-benchmarks/github-pipelines/length{length}_{case_num}"
    output_path = case_dir / "target_multisource_mcts.csv"
    gt_path     = case_dir / "target.csv"

    if not output_path.exists() or not gt_path.exists():
        return False, 0.0

    try:
        df_output = pd.read_csv(output_path, low_memory=False)
        df_gt     = pd.read_csv(gt_path,     low_memory=False)
        # Drop index column from ground truth (matches nodes.py behaviour)
        df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)

        # Suppress print output from compare_tables / compare_tables_matching
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            avg_sim, is_match, _, _ = compare_tables_matching(df_output, df_gt)
        return bool(is_match), float(avg_sim)
    except Exception:
        return False, 0.0


# ===========================================================================
# Per-case evaluation helper
# ===========================================================================

def _eval_script(
    script: Optional[str],
    case_num: int,
    work_dir: Path,
    dry_run: bool,
) -> dict:
    """Run a single script (after path swap) and validate. Returns result dict."""
    if not script:
        return {"has_script": False, "run_ok": False, "correct": False, "sim": 0.0, "error": "no_script"}

    test_script = swap_training_to_test(script)
    if dry_run:
        return {"has_script": True, "run_ok": None, "correct": None, "sim": None, "error": "dry_run"}

    ok, err = run_script(test_script, work_dir)
    if not ok:
        return {"has_script": True, "run_ok": False, "correct": False, "sim": 0.0, "error": err[:100]}

    correct, sim = validate_output(case_num, work_dir)
    return {"has_script": True, "run_ok": True, "correct": correct, "sim": round(sim, 4), "error": ""}


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate run8 L1 training MCTS by running extracted scripts on test data."
    )
    parser.add_argument(
        "--log_dir",
        default="logs_langraph/rag_det_score_run8_l1_training",
        help="Root log directory",
    )
    parser.add_argument(
        "--work_dir", default=".",
        help="Working directory for running scripts (should be project root)",
    )
    parser.add_argument(
        "--cases", nargs="*", type=int,
        help="Specific case numbers to evaluate (default: all 100)",
    )
    parser.add_argument(
        "--output", default="eval_run8_training_results.csv",
        help="Output CSV path",
    )
    parser.add_argument("--dry_run", action="store_true",
                        help="Skip script execution, just extract and report scripts found")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    log_dir  = Path(args.log_dir)
    work_dir = Path(args.work_dir).resolve()

    if not log_dir.exists():
        print(f"[ERROR] Log directory not found: {log_dir}")
        sys.exit(1)

    # Collect case dirs
    case_dirs = sorted(
        d for d in log_dir.iterdir()
        if d.is_dir() and re.match(r'^cases_c\d+$', d.name)
    )
    if args.cases:
        wanted = {f"cases_c{n}" for n in args.cases}
        case_dirs = [d for d in case_dirs if d.name in wanted]

    print(f"Evaluating {len(case_dirs)} cases from {log_dir}")
    if args.dry_run:
        print("  DRY RUN — scripts will NOT be executed")

    all_rows = []

    for case_dir in case_dirs:
        m = re.match(r'cases_c(\d+)', case_dir.name)
        if not m:
            continue
        case_num = int(m.group(1))

        log_files = sorted(case_dir.glob("*.log"))
        if not log_files:
            if args.verbose:
                print(f"  c{case_num}: no .log file — skip")
            continue
        log_file = log_files[0]

        # Parse log
        root, iter_scripts, global_best_script, global_best_score, total_iters = \
            parse_log_with_scripts(log_file)

        if root is None or total_iters == 0:
            if args.verbose:
                print(f"  c{case_num}: parse failed / 0 iters — skip")
            continue

        # Greedy total_reward path
        path = greedy_tr_path(root)
        leaf = path[-1]
        bop  = best_on_path(path)

        leaf_script = get_node_script(leaf, iter_scripts)
        bop_script  = get_node_script(bop,  iter_scripts)

        # Run evaluations
        res_a   = _eval_script(global_best_script, case_num, work_dir, args.dry_run)
        res_bl  = _eval_script(leaf_script,         case_num, work_dir, args.dry_run)
        # BOP: only run separately if it's a different node than the leaf
        if id(bop) != id(leaf) and bop_script != leaf_script:
            res_bop = _eval_script(bop_script, case_num, work_dir, args.dry_run)
        else:
            res_bop = res_bl.copy()  # same script → same result

        row = {
            "case_num":              case_num,
            "total_iters":           total_iters,
            "global_best_score":     round(global_best_score, 4),
            "leaf_best":             round(leaf.best, 4),
            "leaf_best_iter":        leaf.best_iter,
            "leaf_best_is_crit":     leaf.best_is_critique,
            "bop_best":              round(bop.best, 4),
            "bop_best_iter":         bop.best_iter,
            # Method A
            "a_has_script":          res_a["has_script"],
            "a_run_ok":              res_a["run_ok"],
            "a_correct":             res_a["correct"],
            "a_sim":                 res_a["sim"],
            "a_error":               res_a["error"],
            # Method B-leaf
            "bl_has_script":         res_bl["has_script"],
            "bl_run_ok":             res_bl["run_ok"],
            "bl_correct":            res_bl["correct"],
            "bl_sim":                res_bl["sim"],
            "bl_error":              res_bl["error"],
            # Method B-BOP
            "bop_has_script":        res_bop["has_script"],
            "bop_run_ok":            res_bop["run_ok"],
            "bop_correct":           res_bop["correct"],
            "bop_sim":               res_bop["sim"],
        }
        all_rows.append(row)

        if args.verbose:
            a_tag  = ("✓" if res_a["correct"]   else "✗") if res_a["run_ok"]   else "?"
            bl_tag = ("✓" if res_bl["correct"]  else "✗") if res_bl["run_ok"]  else "?"
            bop_tag = ("✓" if res_bop["correct"] else "✗") if res_bop["run_ok"] else "?"
            print(
                f"  c{case_num:3d} iters={total_iters:3d}  "
                f"bs={global_best_score:.4f}  leaf={leaf.best:.4f}  bop={bop.best:.4f}  "
                f"A={a_tag}  BL={bl_tag}  BOP={bop_tag}"
            )

    # ── Summary ──────────────────────────────────────────────────────────────
    n = len(all_rows)
    if n == 0:
        print("No cases processed.")
        return

    def _cnt(key, val=True):
        return sum(1 for r in all_rows if r.get(key) == val)

    has_a   = _cnt("a_has_script")
    has_bl  = _cnt("bl_has_script")
    run_a   = _cnt("a_run_ok")
    run_bl  = _cnt("bl_run_ok")
    ok_a    = _cnt("a_correct")
    ok_bl   = _cnt("bl_correct")
    ok_bop  = _cnt("bop_correct")

    W = 70
    print(f"\n{'='*W}")
    print(f"Run8 L1 Training Evaluation — {n} cases")
    print(f"{'='*W}")
    print(f"  Script extracted   Method A (global best):  {has_a}/{n}")
    print(f"  Script extracted   Method B leaf:           {has_bl}/{n}")
    if not args.dry_run:
        print(f"  Scripts executed   Method A:               {run_a}/{has_a}")
        print(f"  Scripts executed   Method B leaf:          {run_bl}/{has_bl}")
        print(f"{'─'*W}")
        print(f"  Method A  (best training score → test):  {ok_a:3d}/{n}  ({ok_a/n:.1%})")
        print(f"  Method B  (greedy TR leaf → test):       {ok_bl:3d}/{n}  ({ok_bl/n:.1%})")
        print(f"  Method B' (greedy TR BOP → test):        {ok_bop:3d}/{n}  ({ok_bop/n:.1%})")

        both_correct   = _cnt_fn(lambda r: r["a_correct"] and r["bl_correct"], all_rows)
        a_only         = _cnt_fn(lambda r: r["a_correct"] and not r["bl_correct"], all_rows)
        bl_only        = _cnt_fn(lambda r: not r["a_correct"] and r["bl_correct"], all_rows)
        neither        = _cnt_fn(lambda r: not r["a_correct"] and not r["bl_correct"], all_rows)
        print(f"{'─'*W}")
        print(f"  A✓ ∧ BL✓  (both correct)          {both_correct}")
        print(f"  A✓ ∧ BL✗  (A wins)                {a_only}")
        print(f"  A✗ ∧ BL✓  (BL wins)               {bl_only}")
        print(f"  A✗ ∧ BL✗  (both miss)              {neither}")
    print(f"{'='*W}")

    # ── CSV output ────────────────────────────────────────────────────────────
    out_path = Path(args.output)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nDetailed results → {out_path}")


def _cnt_fn(pred, rows):
    return sum(1 for r in rows if pred(r))


if __name__ == "__main__":
    main()
