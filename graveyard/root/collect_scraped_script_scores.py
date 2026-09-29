"""
collect_scraped_script_scores.py
====================================
Scores every script under scraped_scripts/L{1,2,3,4,5,9}/ against its case's
ground truth, producing one CSV row per (length, case, script) with:

  - TRAIN-side score components (value_based_relative_csv_score, mirroring
    what MCTS itself uses as reward): fd_f1 + its precision/recall halves,
    avg_col_score_1, row_count_score, max_missing_score, score_1/score_2/
    row_ratio/true_combined_score, plus a per-column-type leaf-level
    breakdown (avg_float_js/range, avg_int_js/range/nunique/missing,
    avg_id_nunique/missing, avg_cat_prop/nunique/missing, avg_date_score)
    extracted from value_based_relative_csv_score's debug_dict — the finer
    feature set discussed for weight tuning beyond the current flat 4.
  - TEST-side autopipeline validation status: script rewritten to read
    test_N.csv instead of training_N.csv, executed, and its output compared
    to target.csv via compare_tables_matching (is_match).

No redundant work: GT-side FD mining and self-column-map (the two calls that
depend only on ground truth, not on any particular script) are computed ONCE
per case and reused across every script belonging to that case, mirroring
Langraph/mcts_search.py's _gt_score_cache_worker. Filenames already encode
length/case/iter/kind/log-score (c{case}_score{score}_iter{iter}_{kind}.py),
so no log re-parsing is needed.

Parallelized per CASE (not per script) so the GT cache built by a worker is
actually reused by every script in that case before being discarded.

Usage:
  python3 collect_scraped_script_scores.py [--lengths 1 2 3 4 5 9] [--workers 30] [--cases_per_length N]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import argparse
import csv
import io
import re
import sys
import uuid
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent
EVAL_SCORE_DIR = WORK_DIR / "eval_score"
for _p in (str(WORK_DIR), str(EVAL_SCORE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
from tqdm import tqdm

from eval_run8_training import run_script, swap_training_to_test
from validation.hard_match import compare_tables_matching
from eval_score_value_based import value_based_relative_csv_score

import fdtool.fdtool as fdtool
import column_map_utils
from column_map_utils import get_column_map

SCRAPED_DIR = WORK_DIR / "scraped_scripts"
OUTPUT_BASENAME = "target_multisource_mcts.csv"
DEFAULT_OUTPUT = SCRAPED_DIR / "scraped_scripts_scores.csv"

# Mirror eval_score/score.py + Langraph/mcts_search.py's GT-cache constants exactly
MAX_FD_COLS = 52
FD_TIMEOUT = 60
_MAX_SCORE_COLS = 20
_MAX_FD_ROWS = 2000

# Cases whose GT is wider than this are skipped entirely (no FD-mining attempt,
# no script execution) rather than paying for a timeout/truncation that would
# happen anyway.
MAX_GT_COLS_FOR_SCORING = 30

FILENAME_RE = re.compile(
    r"^c(?P<case>\d+)_score(?P<score>[\d.]+)_iter(?P<iter>\d+)_(?P<kind>sim|critique)\.py$"
)

FIELDNAMES = [
    "length", "case_num", "iter", "kind", "log_score",
    # train-side: score_1 components (reward as MCTS would compute it) + leaf breakdown
    "train_run_ok", "train_error",
    "fd_f1", "precision", "recall",
    "avg_col_score_1",
    "n_float_cols", "avg_float_js", "avg_float_range",
    "n_int_cols", "avg_int_js", "avg_int_range", "avg_int_nunique", "avg_int_missing",
    "n_id_cols", "avg_id_nunique", "avg_id_missing",
    "n_cat_cols", "avg_cat_prop", "avg_cat_nunique", "avg_cat_missing",
    "n_date_cols", "avg_date_score",
    "row_count_score", "max_missing_score",
    "score_1", "score_2", "row_ratio", "true_combined_score",
    # test-side: held-out autopipeline validation status
    "test_run_ok", "test_error", "is_match",
]


# ---------------------------------------------------------------------------
# Discovery (fast, runs in main process — filenames already carry everything)
# ---------------------------------------------------------------------------

def discover_cases(lengths, cases_per_length=None):
    """Returns {(length, case_num): [(iter, kind, log_score, path), ...]}."""
    grouped = defaultdict(list)
    for length in lengths:
        length_dir = SCRAPED_DIR / f"L{length}"
        if not length_dir.is_dir():
            continue
        for path in sorted(length_dir.glob("*.py")):
            m = FILENAME_RE.match(path.name)
            if not m:
                continue
            grouped[(length, int(m.group("case")))].append(
                (int(m.group("iter")), m.group("kind"), float(m.group("score")), path)
            )

    if cases_per_length is not None:
        by_length = defaultdict(list)
        for key in grouped:
            by_length[key[0]].append(key)
        keep = set()
        for length, keys in by_length.items():
            keep.update(sorted(keys, key=lambda k: k[1])[:cases_per_length])
        grouped = {k: v for k, v in grouped.items() if k in keep}

    return grouped


# ---------------------------------------------------------------------------
# GT cache: FD mining + self-column-map, computed ONCE per case
# ---------------------------------------------------------------------------

def _run_fdtool_capped(df):
    """Returns ((FDs, E, keys), timed_out)."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fdtool.main, df)
        try:
            return future.result(timeout=FD_TIMEOUT), False
        except FuturesTimeoutError:
            return ([], [], []), True


def build_gt_cache(df_gt_full: pd.DataFrame):
    """Mirrors Langraph/mcts_search.py's _gt_score_cache_worker: mine GT-side
    FDs + self-column-map once; only reduce to 20 cols / 2000 rows if
    full-size FD mining times out. Returns (precomputed_gt, df_gt_for_scoring,
    max_fd_rows)."""
    (FDs_b, E_b, keys_b), timed_out = _run_fdtool_capped(df_gt_full.iloc[:, :MAX_FD_COLS])
    df_gt = df_gt_full
    max_fd_rows = None
    if timed_out:
        df_gt = df_gt_full.iloc[:_MAX_FD_ROWS, :_MAX_SCORE_COLS]
        (FDs_b, E_b, keys_b), _ = _run_fdtool_capped(df_gt.iloc[:, :MAX_FD_COLS])
        max_fd_rows = _MAX_FD_ROWS

    column_map_utils.GLOBAL_SUMMARY = None
    self_col_count = len(get_column_map(df_gt, df_gt))

    precomputed_gt = {
        "FDs_b": FDs_b, "E_b": E_b, "keys_b": keys_b,
        "self_col_count": self_col_count,
        "max_fd_rows": max_fd_rows,
    }
    return precomputed_gt, df_gt, max_fd_rows


# ---------------------------------------------------------------------------
# Leaf-feature extraction from value_based_relative_csv_score's debug_dict
# ---------------------------------------------------------------------------

def _mean(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def _extract_leaf_features(debug: dict) -> dict:
    fd = debug.get("fd", {})
    per_col = (debug.get("column_scores") or {}).get("per_column") or {}

    floats, ints, ids, cats, dates = [], [], [], [], []
    for cd in per_col.values():
        t = cd.get("type")
        if t == "numeric":
            (ints if cd.get("nunique_sim") is not None else floats).append(cd)
        elif t == "id":
            ids.append(cd)
        elif t == "categorical":
            cats.append(cd)
        elif t in ("date_as_numeric", "date_mismatch"):
            dates.append(cd)  # mismatch's column_score is a hard 0, folded in like today

    return {
        "precision": fd.get("precision"),
        "recall": fd.get("recall"),
        "n_float_cols": len(floats),
        "avg_float_js": _mean(c.get("js_similarity") for c in floats),
        "avg_float_range": _mean(c.get("range_overlap") for c in floats),
        "n_int_cols": len(ints),
        "avg_int_js": _mean(c.get("js_similarity") for c in ints),
        "avg_int_range": _mean(c.get("range_overlap") for c in ints),
        "avg_int_nunique": _mean(c.get("nunique_sim") for c in ints),
        "avg_int_missing": _mean(c.get("missing_sim") for c in ints),
        "n_id_cols": len(ids),
        "avg_id_nunique": _mean(c.get("nunique_sim") for c in ids),
        "avg_id_missing": _mean(c.get("missing_sim") for c in ids),
        "n_cat_cols": len(cats),
        "avg_cat_prop": _mean(c.get("cat_score") for c in cats),
        "avg_cat_nunique": _mean(c.get("nunique_sim") for c in cats),
        "avg_cat_missing": _mean(c.get("missing_sim") for c in cats),
        "n_date_cols": len(dates),
        "avg_date_score": _mean(c.get("column_score") for c in dates),
    }


# ---------------------------------------------------------------------------
# Per-script execution
# ---------------------------------------------------------------------------

def _run_variant(script: str, case_dir: Path, tag: str):
    """Run one script variant to a unique output filename (avoids collisions
    between the train/test variant of the same script, and between scripts of
    the same case run back-to-back). Returns (ok, error, output_path)."""
    if OUTPUT_BASENAME not in script:
        return False, "no_standard_output_filename_in_script", None
    unique_name = f"target_multisource_mcts_{tag}_{uuid.uuid4().hex[:12]}.csv"
    rewritten = script.replace(OUTPUT_BASENAME, unique_name)
    output_path = case_dir / unique_name
    ok, err = run_script(rewritten, WORK_DIR)
    if not ok:
        return False, err[:150], output_path
    if not output_path.exists():
        return False, "missing_output", output_path
    return True, "", output_path


# ---------------------------------------------------------------------------
# Per-case worker (subprocess): build the GT cache once, reuse across every
# script in this case, then discard it.
# ---------------------------------------------------------------------------

def process_case(task) -> list:
    length, case_num, entries = task
    case_dir = WORK_DIR / f"autopipeline-benchmarks/github-pipelines/length{length}_{case_num}"
    gt_path = case_dir / "target.csv"
    rows = []

    def _fallback_rows(error):
        return [{
            "length": length, "case_num": case_num, "iter": it, "kind": kind, "log_score": log_score,
            "train_run_ok": False, "train_error": error,
            "test_run_ok": False, "test_error": error,
        } for it, kind, log_score, _ in entries]

    if not gt_path.exists():
        return _fallback_rows("missing_ground_truth")

    try:
        df_gt_full = pd.read_csv(gt_path, low_memory=False)
        df_gt_full = df_gt_full.drop(columns=df_gt_full.columns[0], axis=1)
    except Exception as e:
        return _fallback_rows(f"gt_load_failed: {str(e)[:150]}")

    # Discard the whole case up front if GT is too wide — skips both the
    # (up to 2x 60s) FD-mining attempt and every script execution for it,
    # rather than paying for a truncated/timed-out attempt anyway.
    n_gt_cols = len(df_gt_full.columns)
    if n_gt_cols > MAX_GT_COLS_FOR_SCORING:
        return _fallback_rows(f"discarded_gt_too_wide_{n_gt_cols}cols")

    try:
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            precomputed_gt, df_gt_scoring, max_fd_rows = build_gt_cache(df_gt_full)
    except Exception as e:
        return _fallback_rows(f"gt_cache_failed: {str(e)[:150]}")

    for it, kind, log_score, path in entries:
        row = {
            "length": length, "case_num": case_num, "iter": it, "kind": kind, "log_score": log_score,
            "train_run_ok": False, "train_error": "", "test_run_ok": False, "test_error": "",
        }
        train_output_path = None
        test_output_path = None
        try:
            script = path.read_text()

            # ── TRAIN run: script as-is → score components via the shared GT cache ──
            ok, err, train_output_path = _run_variant(script, case_dir, "train")
            row["train_run_ok"] = ok
            row["train_error"] = err
            if ok:
                try:
                    df_output = pd.read_csv(train_output_path, low_memory=False)
                    if max_fd_rows is not None:
                        df_output = df_output.iloc[:max_fd_rows]  # symmetric row cap, matches nodes.py
                    buf = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(buf):
                        _, _, _, fd_f1, true_combined_score, debug = value_based_relative_csv_score(
                            df_output, df_gt_scoring, precomputed_gt=precomputed_gt
                        )
                    row.update({
                        "fd_f1": fd_f1,
                        "avg_col_score_1": debug.get("avg_col_score_1"),
                        "row_count_score": debug.get("row_count_score"),
                        "max_missing_score": debug.get("max_missing_score"),
                        "score_1": debug.get("score_1"),
                        "score_2": debug.get("score_2"),
                        "row_ratio": debug.get("row_ratio"),
                        "true_combined_score": true_combined_score,
                    })
                    row.update(_extract_leaf_features(debug))
                except Exception as e:
                    row["train_error"] = f"score_failed: {str(e)[:150]}"

            # ── TEST run: training_N.csv -> test_N.csv → autopipeline validation ──
            try:
                test_script = swap_training_to_test(script)
                ok, err, test_output_path = _run_variant(test_script, case_dir, "test")
                row["test_run_ok"] = ok
                row["test_error"] = err
                if ok:
                    try:
                        df_test_output = pd.read_csv(test_output_path, low_memory=False)
                        buf = io.StringIO()
                        with redirect_stdout(buf), redirect_stderr(buf):
                            _, is_match, _, _ = compare_tables_matching(df_test_output, df_gt_full)
                        row["is_match"] = bool(is_match)
                    except Exception as e:
                        row["test_error"] = f"score_failed: {str(e)[:150]}"
            except Exception as e:
                row["test_error"] = f"unexpected: {str(e)[:150]}"
        except Exception as e:
            row["train_error"] = row["train_error"] or f"unexpected: {str(e)[:150]}"
        finally:
            for p in (train_output_path, test_output_path):
                if p is not None:
                    try:
                        p.unlink(missing_ok=True)
                    except Exception:
                        pass
            rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lengths", nargs="*", type=int, default=[1, 2, 3, 4, 5, 9])
    parser.add_argument("--cases_per_length", type=int, default=None,
                         help="Limit to first N cases per length (for smoke testing)")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    print("Discovering scraped scripts...", flush=True)
    grouped = discover_cases(args.lengths, args.cases_per_length)
    tasks = [(length, case_num, entries) for (length, case_num), entries in grouped.items()]
    n_scripts = sum(len(e) for e in grouped.values())
    print(f"{len(tasks)} cases, {n_scripts} scripts across lengths {args.lengths}", flush=True)

    out_path = Path(args.output)
    n_train_ok = n_test_ok = n_match = n_rows = 0
    discarded_cases = set()
    with out_path.open("w", newline="") as f, \
         ProcessPoolExecutor(max_workers=args.workers) as executor:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()

        futures = {executor.submit(process_case, t): t for t in tasks}
        pbar = tqdm(as_completed(futures), total=len(tasks), unit="case")
        for future in pbar:
            length, case_num, entries = futures[future]
            try:
                rows = future.result()
            except Exception as e:
                rows = [{
                    "length": length, "case_num": case_num, "iter": it, "kind": kind, "log_score": log_score,
                    "train_run_ok": False, "train_error": f"worker_exception: {str(e)[:150]}",
                    "test_run_ok": False, "test_error": f"worker_exception: {str(e)[:150]}",
                } for it, kind, log_score, _ in entries]

            for row in rows:
                writer.writerow(row)
                n_rows += 1
                if row.get("train_run_ok"):
                    n_train_ok += 1
                if row.get("test_run_ok"):
                    n_test_ok += 1
                if row.get("is_match"):
                    n_match += 1
                if str(row.get("train_error", "")).startswith("discarded_gt_too_wide"):
                    discarded_cases.add((length, case_num))
            f.flush()
            pbar.set_postfix(rows=n_rows, train_ok=n_train_ok, test_ok=n_test_ok, is_match=n_match)

    print(f"\n{n_rows} script rows -> {out_path}")
    print(f"  cases discarded (GT > {MAX_GT_COLS_FOR_SCORING} cols): {len(discarded_cases)}/{len(tasks)}")
    print(f"  train_run_ok: {n_train_ok}/{n_rows}")
    print(f"  test_run_ok:  {n_test_ok}/{n_rows}")
    print(f"  is_match (correct on test): {n_match}/{n_rows}")


if __name__ == "__main__":
    main()
