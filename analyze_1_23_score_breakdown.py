"""
Case 1_23 — training score distribution breakdown for each of the 10 unique det_score_value scripts.
Shows how each sub-component contributes to the final score.
Output: 1_23_score_breakdown.txt
"""

import re, sys, os, subprocess, tempfile
sys.path.insert(0, ".")

import pandas as pd
import eval_score_value_based as vb

LOG_PATH = "logs_langraph/rag_det_score_t1_train/cases_t1_train_1_23/1_target23_MCTS_20260626_070918.log"
DATA_DIR = "autopipeline-benchmarks/github-pipelines/length1_23"
GT_PATH  = f"{DATA_DIR}/target.csv"
OUT_FILE = f"{DATA_DIR}/target_multisource_mcts.csv"
OUT_TXT  = "1_23_score_breakdown.txt"

SCORE_DEFINITION = """\
DET_SCORE_VALUE — Score Definition
===================================
The det_score_value reward uses value_based_relative_csv_score, which computes:

  true_combined_score = (fd_f1 + avg_column_score) / 2

  Components
  ──────────
  1. FD_F1 (Functional Dependency F1)
       Mines functional dependencies (FDs) from both the generated and ground-truth
       tables, then computes F1 = 2*precision*recall / (precision+recall).
       FD: a set of columns LHS that uniquely determines column RHS.
       A perfect FD match means the generated table has the same structural
       dependency patterns as the ground truth.

  2. COLUMN_RATIO
       Fraction of GT columns that were successfully mapped to a generated column
       via Jaccard similarity on unique values (categorical) or numeric range/JS.
       E.g. 2/2 columns mapped → ratio = 1.0.

  3. PER-COLUMN SCORE  (per GT column, then averaged → avg_column_score)
       • Numeric column:  column_score = 0.5 × (js_similarity + range_overlap)
           – JS_similarity:    1 - JensenShannon(dist_gen, dist_gt) — measures how
                               similar the value distributions are (0=identical, 1=max diff)
           – Range_overlap:    overlap of [min, max] intervals between gen and gt column
       • Categorical column: column_score = MinHash Jaccard on unique string values

  Final formula:
      true_combined_score = (fd_f1 + avg_column_score) / 2

  NOTE: This score operates on COLUMN DISTRIBUTIONS, not row-by-row values,
  so it can be high even when row counts differ between generated and GT tables.
  A script that produces the right column shapes/ranges but wrong row count will
  still score well on det_score_value while failing a hard-match (exact) check.
"""

# ── 1. Extract scripts + logged det_score ─────────────────────────────────────
lines = open(LOG_PATH).readlines()
scripts = []
in_s, buf = False, []

for i, line in enumerate(lines):
    if re.match(r"^```[Pp]ython\s*$", line.strip()):
        buf = []; in_s = True; continue
    if in_s:
        if line.strip() == "```":
            code = "".join(buf).strip()
            if code:
                logged = None
                for j in range(i+1, min(i+25, len(lines))):
                    m = re.search(r"execute_and_score.*reward=([\d.]+)", lines[j])
                    if m: logged = float(m.group(1)); break
                scripts.append((len(scripts)+1, logged, code))
            in_s = False; buf = []
        else:
            buf.append(line)

# One representative per unique logged score
scored = [(idx, sc, code) for idx, sc, code in scripts
          if sc is not None and not code.strip().startswith('<')]
seen, representatives = set(), []
for idx, sc, code in scored:
    if sc not in seen:
        seen.add(sc)
        representatives.append((idx, sc, code))
representatives.sort(key=lambda x: x[1])

# ── 2. Load ground truth ──────────────────────────────────────────────────────
df_gt = pd.read_csv(GT_PATH, low_memory=False)
df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)


def run_script(code):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
        tf.write(code); tmp = tf.name
    try:
        r = subprocess.run(["python3", tmp], capture_output=True, timeout=30, cwd=".")
        if r.returncode != 0:
            return None, r.stderr.decode()[:200].strip()
        if not os.path.exists(OUT_FILE):
            return None, "no output file"
        df_out = pd.read_csv(OUT_FILE, low_memory=False)
        return df_out, None
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception as e:
        return None, str(e)
    finally:
        try: os.unlink(tmp)
        except: pass


def get_breakdown(df_out, df_gt):
    """Return the full 6-tuple + debug_dict from value_based_relative_csv_score."""
    fd_ratio, col_ratio, combined, fd_f1, true_combined, debug = \
        vb.value_based_relative_csv_score(df_out, df_gt)
    return fd_ratio, col_ratio, combined, fd_f1, true_combined, debug


# ── 3. Run + collect breakdowns ───────────────────────────────────────────────
breakdowns = []
for script_num, logged_det, code in representatives:
    df_out, err = run_script(code)
    if err or df_out is None:
        breakdowns.append((script_num, logged_det, None, err))
        continue
    try:
        breakdown = get_breakdown(df_out, df_gt)
        breakdowns.append((script_num, logged_det, breakdown, None))
    except Exception as e:
        breakdowns.append((script_num, logged_det, None, str(e)))


# ── 4. Write report ───────────────────────────────────────────────────────────
def fmt(v, decimals=4):
    if v is None: return "N/A"
    if isinstance(v, float): return f"{v:.{decimals}f}"
    return str(v)

with open(OUT_TXT, "w") as f:

    f.write("Case 1_23 — Training Score Distribution Breakdown\n")
    f.write("Experiment: rag_det_score_t1_train\n")
    f.write(f"GT columns: {list(df_gt.columns)}  |  GT rows: {len(df_gt)}\n")
    f.write("\n")
    f.write(SCORE_DEFINITION)
    f.write("\n\n")

    # ── Summary table ────────────────────────────────────────────────────────
    f.write("=" * 110 + "\n")
    f.write("SUMMARY TABLE (training data)\n")
    f.write("=" * 110 + "\n")
    hdr = (f"{'Script#':>8}  {'LoggedDet':>10}  {'FD_F1':>7}  {'ColRatio':>9}  "
           f"{'AvgColScore':>12}  {'TrueCombined':>13}  "
           f"{'Col:customer_id':>16}  {'Col:amount':>11}  "
           f"{'GenRows':>8}  {'GTRows':>7}")
    f.write(hdr + "\n")
    f.write("-" * len(hdr) + "\n")

    for script_num, logged_det, bd, err in breakdowns:
        if bd is None:
            f.write(f"{'#'+str(script_num):>8}  {fmt(logged_det):>10}  {'ERROR':>7}  "
                    f"{'—':>9}  {'—':>12}  {'—':>13}  {'—':>16}  {'—':>11}  "
                    f"{'—':>8}  {'—':>7}  {err}\n")
            continue
        fd_ratio, col_ratio, combined, fd_f1, true_combined, debug = bd
        col_scores = debug.get("column_scores", {}).get("per_column", {})
        avg_col    = debug.get("column_scores", {}).get("avg_column_score", None)
        cid_score  = col_scores.get("customer_id", {}).get("column_score")
        amt_score  = col_scores.get("amount", {}).get("column_score")
        # row counts from distribution stats (gen_stats reflects generated table)
        dist = debug.get("distribution", {}).get("per_column", {})
        gen_rows_approx = "?"  # can't recover exact row count from debug, use df_out shape
        f.write(f"{'#'+str(script_num):>8}  {fmt(logged_det):>10}  {fmt(fd_f1):>7}  "
                f"{fmt(col_ratio):>9}  {fmt(avg_col):>12}  {fmt(true_combined):>13}  "
                f"{fmt(cid_score):>16}  {fmt(amt_score):>11}\n")

    f.write("\n")

    # ── Detailed breakdown per script ─────────────────────────────────────────
    f.write("=" * 110 + "\n")
    f.write("DETAILED BREAKDOWN PER SCRIPT (training data)\n")
    f.write("=" * 110 + "\n\n")

    for script_num, logged_det, bd, err in breakdowns:
        (_, _, code) = next((x for x in representatives if x[0] == script_num), (None,None,""))

        f.write(f"{'─'*80}\n")
        f.write(f"Script #{script_num}   logged_det_train = {logged_det}\n")
        f.write(f"{'─'*80}\n")

        if bd is None:
            f.write(f"  *** FAILED TO RUN: {err} ***\n\n")
            f.write("  Code:\n")
            for line in code.split("\n"):
                f.write(f"    {line}\n")
            f.write("\n")
            continue

        fd_ratio, col_ratio, combined, fd_f1, true_combined, debug = bd

        # Run again to get row count
        df_out2, _ = run_script(code)
        gen_rows = len(df_out2) if df_out2 is not None else "?"

        f.write(f"\n  ┌─ FINAL SCORE ──────────────────────────────────────────────────\n")
        f.write(f"  │  true_combined_score = (fd_f1 + avg_column_score) / 2\n")
        f.write(f"  │                      = ({fmt(fd_f1)} + {fmt(debug['column_scores']['avg_column_score'])}) / 2\n")
        f.write(f"  │                      = {fmt(true_combined)}\n")
        f.write(f"  │  Generated rows: {gen_rows}   |   GT rows: {len(df_gt)}\n")
        f.write(f"  └───────────────────────────────────────────────────────────────\n\n")

        f.write(f"  ┌─ FD (Functional Dependency) Score ────────────────────────────\n")
        fd_info = debug.get("fd", {})
        f.write(f"  │  fd_f1      = {fmt(fd_info.get('f1'))}\n")
        f.write(f"  │  precision  = {fmt(fd_info.get('precision'))}\n")
        f.write(f"  │  recall     = {fmt(fd_info.get('recall'))}\n")
        fds_a = fd_info.get("A", {}).get("fds", [])
        fds_b = fd_info.get("B", {}).get("fds", [])
        f.write(f"  │  Generated FDs : {[str(x['lhs'])+'→'+x['rhs'] for x in fds_a]}\n")
        f.write(f"  │  GT FDs        : {[str(x['lhs'])+'→'+x['rhs'] for x in fds_b]}\n")
        fps = fd_info.get("false_positives", [])
        fns = fd_info.get("false_negatives", [])
        if fps: f.write(f"  │  False positives (extra FDs in gen): {fps}\n")
        if fns: f.write(f"  │  False negatives (missing FDs):      {fns}\n")
        f.write(f"  └───────────────────────────────────────────────────────────────\n\n")

        f.write(f"  ┌─ Column Mapping ──────────────────────────────────────────────\n")
        f.write(f"  │  column_ratio = {fmt(col_ratio)}  ({int(col_ratio * len(df_gt.columns))}/{len(df_gt.columns)} GT columns mapped)\n")
        jcm = debug.get("jaccard_column_map", [])
        for entry in jcm:
            f.write(f"  │    GT '{entry['gt_col']}' ← Gen '{entry['gen_col']}'  jaccard={fmt(entry['jaccard'])}\n")
        f.write(f"  └───────────────────────────────────────────────────────────────\n\n")

        f.write(f"  ┌─ Per-Column Scores ────────────────────────────────────────────\n")
        col_scores = debug.get("column_scores", {}).get("per_column", {})
        for col, cs in col_scores.items():
            ctype = cs.get("type", "?")
            cscore = cs.get("column_score")
            f.write(f"  │  Column '{col}'  (type={ctype})\n")
            f.write(f"  │    column_score = {fmt(cscore)}")
            if ctype == "numeric":
                js = cs.get("js_similarity")
                ro = cs.get("range_overlap")
                f.write(f"   =  0.5 × (js_similarity={fmt(js)} + range_overlap={fmt(ro)})\n")
                gen_s = cs.get("gen_stats", {})
                gt_s  = cs.get("gt_stats", {})
                f.write(f"  │    Gen  stats: min={gen_s.get('min')}  max={gen_s.get('max')}  mean={fmt(gen_s.get('mean'),2)}\n")
                f.write(f"  │    GT   stats: min={gt_s.get('min')}   max={gt_s.get('max')}   mean={fmt(gt_s.get('mean'),2)}\n")
            else:
                f.write(f"  (MinHash Jaccard on unique values)\n")
        avg_cs = debug.get("column_scores", {}).get("avg_column_score")
        f.write(f"  │\n")
        f.write(f"  │  avg_column_score = {fmt(avg_cs)}\n")
        f.write(f"  └───────────────────────────────────────────────────────────────\n\n")

        f.write("  Code:\n")
        for line in code.split("\n"):
            f.write(f"    {line}\n")
        f.write("\n\n")

print(f"Report written to: {OUT_TXT}")
