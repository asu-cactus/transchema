"""
For case 1_23: find the 10 unique det_score_value scores, pick one script per score,
run each on training and test data, compute det_score_value + partial fuzzy for both.
Output written to 1_23_unique_score_analysis.txt
"""

import re, sys, os, subprocess, tempfile
sys.path.insert(0, ".")

import pandas as pd
from validation.fuzzy_match import compare_tables_fuzzy
import eval_score_value_based as vb

LOG_PATH = "logs_langraph/rag_det_score_t1_train/cases_t1_train_1_23/1_target23_MCTS_20260626_070918.log"
DATA_DIR = "autopipeline-benchmarks/github-pipelines/length1_23"
GT_PATH  = f"{DATA_DIR}/target.csv"
OUT_FILE = f"{DATA_DIR}/target_multisource_mcts.csv"
OUT_TXT  = "1_23_unique_score_analysis.txt"

# ── 1. Extract scripts + logged det_score ─────────────────────────────────────
lines = open(LOG_PATH).readlines()
scripts = []  # (script_idx, logged_det, code)
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

# ── 2. Pick one script per unique logged score (skip None / placeholders) ──────
scored = [(idx, sc, code) for idx, sc, code in scripts
          if sc is not None and not code.strip().startswith('<')]
seen, representatives = set(), []
for idx, sc, code in scored:
    if sc not in seen:
        seen.add(sc)
        representatives.append((idx, sc, code))
representatives.sort(key=lambda x: x[1])  # sort by score ascending

print(f"Total scripts: {len(scripts)}")
print(f"Unique logged scores: {len(representatives)}")
for idx, sc, _ in representatives:
    print(f"  score={sc}  from script #{idx}")

# ── 3. Load ground truth ──────────────────────────────────────────────────────
df_gt = pd.read_csv(GT_PATH, low_memory=False)
df_gt = df_gt.drop(columns=df_gt.columns[0], axis=1)


def run_and_score(code, split):
    """Run script on given split, return (det_score, partial_fuzzy, is_correct, error)."""
    if split == "test":
        code = re.sub(r'training_(\d+)\.csv', r'test_\1.csv', code)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
        tf.write(code); tmp = tf.name

    try:
        r = subprocess.run(
            ["python3", tmp], capture_output=True, timeout=30,
            cwd=os.path.abspath(".")
        )
        if r.returncode != 0:
            return None, None, False, r.stderr.decode()[:120].strip()

        if not os.path.exists(OUT_FILE):
            return None, None, False, "no output file"

        df_out = pd.read_csv(OUT_FILE, low_memory=False)

        # det_score_value
        try:
            _, _, _, _, det, _ = vb.value_based_relative_csv_score(df_out, df_gt)
        except Exception as e:
            det = None

        # partial fuzzy
        try:
            partial, _ = compare_tables_fuzzy(df_out, df_gt)
        except Exception as e:
            partial = None

        # hard correct (partial == 1.0 means all cols matched at exact row length)
        is_correct = (partial is not None and partial >= 1.0
                      and len(df_out) == len(df_gt))

        return det, partial, is_correct, None

    except subprocess.TimeoutExpired:
        return None, None, False, "timeout"
    except Exception as e:
        return None, None, False, str(e)[:80]
    finally:
        try: os.unlink(tmp)
        except: pass


# ── 4. Run analysis ───────────────────────────────────────────────────────────
rows = []
for script_num, logged_det, code in representatives:
    print(f"\nScript #{script_num}  logged_det={logged_det}")
    det_tr, par_tr, ok_tr, err_tr = run_and_score(code, "training")
    det_te, par_te, ok_te, err_te = run_and_score(code, "test")
    rows.append({
        "script_num":   script_num,
        "logged_det_train": logged_det,
        "det_train":    round(det_tr, 4) if det_tr is not None else "ERROR",
        "partial_train": round(par_tr, 4) if par_tr is not None else "ERROR",
        "correct_train": ok_tr,
        "det_test":     round(det_te, 4) if det_te is not None else "ERROR",
        "partial_test": round(par_te, 4) if par_te is not None else "ERROR",
        "correct_test": ok_te,
        "error":        (err_tr or err_te or "").replace("\n", " ")[:100],
        "code_preview": code.replace("\n", " ")[:120],
    })
    print(f"  train: det={det_tr}  partial={par_tr}  ok={ok_tr}  err={err_tr}")
    print(f"  test:  det={det_te}  partial={par_te}  ok={ok_te}  err={err_te}")


# ── 5. Write TXT report ───────────────────────────────────────────────────────
with open(OUT_TXT, "w") as f:
    f.write("Case 1_23 — Unique Det_Score_Value Analysis\n")
    f.write("Experiment: rag_det_score_t1_train\n")
    f.write(f"Ground truth: {GT_PATH}  shape={df_gt.shape}  cols={list(df_gt.columns)}\n")
    f.write(f"Total scripts generated: {len(scripts)}\n")
    f.write(f"Unique logged det_score_values: {len(representatives)}\n")
    f.write("=" * 100 + "\n\n")

    col_w = [10, 18, 12, 14, 14, 12, 14, 14, 8]
    headers = ["Script #", "Logged_Det_Train", "Det_Train", "Partial_Train",
               "Correct_Train", "Det_Test", "Partial_Test", "Correct_Test", "Error?"]
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_w))
    f.write(header_line + "\n")
    f.write("-" * len(header_line) + "\n")

    for r in rows:
        vals = [
            str(r["script_num"]),
            str(r["logged_det_train"]),
            str(r["det_train"]),
            str(r["partial_train"]),
            str(r["correct_train"]),
            str(r["det_test"]),
            str(r["partial_test"]),
            str(r["correct_test"]),
            "YES" if r["error"] else "",
        ]
        f.write("  ".join(v.ljust(w) for v, w in zip(vals, col_w)) + "\n")

    f.write("\n" + "=" * 100 + "\n\n")
    f.write("Scripts detail (code for each representative):\n\n")

    for r, (script_num, logged_det, code) in zip(rows, representatives):
        f.write(f"{'─'*80}\n")
        f.write(f"Script #{script_num}  |  logged_det_train={logged_det}\n")
        f.write(f"  det_train={r['det_train']}   partial_train={r['partial_train']}   correct_train={r['correct_train']}\n")
        f.write(f"  det_test={r['det_test']}    partial_test={r['partial_test']}    correct_test={r['correct_test']}\n")
        if r["error"]:
            f.write(f"  error: {r['error']}\n")
        f.write("\n")
        f.write(code)
        f.write("\n\n")

print(f"\nReport written to: {OUT_TXT}")
