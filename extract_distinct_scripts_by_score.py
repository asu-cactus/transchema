"""
extract_distinct_scripts_by_score.py
===========================
Scrapes the gpt-4.1-mini / weight-set-1 / training-split experiment logs for
L1, L2, L3, L4, L5, L9 and, for every case, extracts every DISTINCT script --
distinctness defined by distinct SCORE (rounded to 4 decimals), not by exact
script text (a script that recurs with the same score is not re-saved; two
different scripts that happen to land on the same rounded score count as one).

Writes each distinct script to scraped_scripts/L{length}/c{case}_score{score}_iter{iter}_{kind}.py

Usage: python3 extract_distinct_scripts_by_score.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import glob
from pathlib import Path

sys.path.insert(0, ".")
from analyze_run8_failed_case_scripts import extract_all_scored_scripts

LOG_DIRS = {
    1: ("logs_langraph/l1_weights_full_weightset1", list(range(100))),
    2: ("logs_langraph/l2_weights_100cases_weightset1", list(range(100))),
    3: ("logs_langraph/l3_weights_weightset1", [c for c in range(101) if c != 30]),
    4: ("logs_langraph/l4_weights_full_weightset1", list(range(100))),
    5: ("logs_langraph/l5_weights_weightset1", list(range(98))),
    9: ("logs_langraph/l9_weights_full_weightset1", list(range(101))),
}

OUT_ROOT = Path("scraped_scripts")


def main():
    grand_total_scripts = 0
    grand_total_cases = 0
    grand_missing_cases = 0

    for length, (log_dir, cases) in LOG_DIRS.items():
        out_dir = OUT_ROOT / f"L{length}"
        out_dir.mkdir(parents=True, exist_ok=True)

        n_cases_with_logs = 0
        n_scripts_this_length = 0

        for case_num in cases:
            files = sorted(glob.glob(f"{log_dir}/cases_c{case_num}/*.log"))
            if not files:
                grand_missing_cases += 1
                continue
            log_file = Path(files[-1])
            entries = extract_all_scored_scripts(log_file)
            if not entries:
                grand_missing_cases += 1
                continue

            n_cases_with_logs += 1
            seen_scores = {}  # rounded score -> (iter, kind, script)
            for it, kind, script, score in entries:
                r = round(score, 4)
                if r not in seen_scores:
                    seen_scores[r] = (it, kind, script)

            for r, (it, kind, script) in seen_scores.items():
                fname = f"c{case_num}_score{r:.4f}_iter{it}_{kind}.py"
                (out_dir / fname).write_text(script)
                n_scripts_this_length += 1

        print(f"L{length}: {n_cases_with_logs}/{len(cases)} cases had logs, "
              f"{n_scripts_this_length} distinct-by-score scripts written to {out_dir}/")
        grand_total_scripts += n_scripts_this_length
        grand_total_cases += n_cases_with_logs

    print(f"\nTOTAL: {grand_total_cases} cases with logs, {grand_missing_cases} cases with no log/no entries, "
          f"{grand_total_scripts} distinct-by-score scripts written under {OUT_ROOT}/")


if __name__ == "__main__":
    main()
