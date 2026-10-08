"""
Re-scores BAT smart_building_v2 cases whose MCTS search finished but whose score was lost.

Before run_smartbuilding_v2_parallel.sh gave every case a private predict dir, concurrent
workers overwrote each other's case_by_case_summary.csv, so some cases were searched
successfully (their length{G}/length{G}_{P}.json is still in the result dir, because cleanup
only runs after a score is read) but never scored. This re-runs the SAME evaluator command
run_cases_iteratively.py uses, one case at a time (no race), and writes each row into
<predict_dir>/g{G}_c{P}/master_results_{G}.csv -- the layout the launcher now produces.

    python3 rescore_unscored_cases.py dmx-gpt-oss-120b execution_20260918_123612
"""
import csv
import glob
import os
import re
import subprocess
import sys

BAT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BAT_DIR)
BASE_PATH = os.path.join(os.path.dirname(BAT_DIR), "autopipeline-benchmarks", "smartbuilding-pipelines-v2-split")

model, execution = sys.argv[1], sys.argv[2]
result_dir = f"result/smart_building_v2/{model}/{execution}"
predict_dir = f"predict/smart_building_v2/{model}/{execution}"

todo = []
for f in glob.glob(f"{result_dir}/length*/length*_*.json"):
    m = re.search(r"length(\d+)/length\d+_(\d+)\.json$", f)
    todo.append((int(m.group(1)), int(m.group(2))))
todo.sort()
print(f"{len(todo)} unscored case(s) in {result_dir}")

for group, pos in todo:
    out = f"{predict_dir}/g{group}_c{pos}"
    os.makedirs(out, exist_ok=True)
    cmd = ["python3", "src/utils/evaluator.py",
           "--json_folder", result_dir, "--data_folder", BASE_PATH, "--output_base", out,
           "--length_types", str(group), "--start_num", str(pos), "--end_num", str(pos + 1),
           "--data_type", "auto_pipeline", "--model_name", model, "--validation", "autopipeline"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    src = os.path.join(out, "case_by_case_summary.csv")
    if proc.returncode != 0 or not os.path.exists(src):
        print(f"length{group}_{pos}: EVALUATOR FAILED (rc={proc.returncode})", proc.stderr[-200:])
        continue
    rows = [r for r in csv.DictReader(open(src)) if r["case_id"] == f"length{group}_{pos}"]
    if not rows:
        print(f"length{group}_{pos}: no row produced")
        continue
    with open(os.path.join(out, f"master_results_{group}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerow(rows[0])
    print(f"length{group}_{pos}: accuracy={rows[0]['accuracy']} tokens={rows[0]['prompt_tokens']}/{rows[0]['completion_tokens']}")
