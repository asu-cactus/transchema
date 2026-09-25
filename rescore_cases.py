"""
rescore_cases.py

Re-scores cases from a JSON log directory using three scoring formulas and
compares each against is_correct to find which is most in sync.

Formulas:
  score_A = (fd_f1 + col_ratio + js_sim + range_overlap) / 4
  score_B = (fd_f1 + col_ratio) / 2
  score_C = (fd_f1 + js_sim + range_overlap) / 3

For each formula, prints a 2x2 confusion matrix:
  score=1.0 vs score<1.0  x  is_correct=True vs is_correct=False

Usage:
    python rescore_cases.py \
        --json_dir <path_to_jsons_dir> \
        --cases 1_9 1_18 1_22 ...  \
        --output rescore_results.csv

    # To run on ALL cases in the directory, omit --cases
    python rescore_cases.py --json_dir <path> --output rescore_results.csv
"""

import argparse
import io
import json
import os
import sys
import glob
from contextlib import redirect_stdout, redirect_stderr

import pandas as pd

# Ensure eval_score is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'eval_score'))
sys.path.insert(0, SCRIPT_DIR)
os.chdir(SCRIPT_DIR)

from eval_score.score import relative_csv_score


def rescore_json(json_path: str, iterations: list[int] | None = None) -> list[dict]:
    """
    Re-score all (or selected) iterations from a single case JSON.

    Returns a list of result dicts, one per iteration.
    """
    with open(json_path) as f:
        data = json.load(f)

    case = data['case']
    results = []

    # Find the case folder from any .csv path in any entry's code
    import re as _re
    case_dir = None
    for it in data['iterations']:
        for entry_key in ['ms'] + [c.get('type', f'critique_{i}') for i, c in enumerate(it.get('critiques', []))]:
            code = it.get('ms', {}).get('code', '') if entry_key == 'ms' else ''
            if not code:
                for c in it.get('critiques', []):
                    code = c.get('code', '')
                    if code:
                        break
            m = _re.search(r'["\']([^"\']*github-pipelines/length\d+_\d+)/', code)
            if m:
                case_dir = m.group(1)
                break
        if case_dir:
            break

    def _error_rows(case, data, error_msg, iterations):
        """Generate error entries for every ms/critique in the JSON so nothing is missing from the CSV."""
        rows = []
        for it in data['iterations']:
            itr = it['iteration']
            if iterations and itr not in iterations:
                continue
            for source_label, entry in [('ms', it.get('ms', {}))] + \
                    [(c.get('type', f'critique_{i}'), c) for i, c in enumerate(it.get('critiques', []))]:
                rows.append({
                    'case': case, 'iteration': itr, 'source': source_label,
                    'old_score': entry.get('score'), 'fd_f1': None, 'col_ratio': None,
                    'js_sim': None, 'range_overlap': None, 'wasserstein_sim': None,
                    'score_a': None, 'score_b': None, 'score_c': None,
                    'is_correct': entry.get('is_correct'), 'error': error_msg,
                })
        return rows

    if not case_dir:
        print(f"[WARN] {case}: could not detect case directory from code.")
        return _error_rows(case, data, 'could not detect case directory from code', iterations)

    gt_path = os.path.join(case_dir, 'target.csv')
    if not os.path.exists(gt_path):
        print(f"[WARN] {case}: ground truth not found at {gt_path}.")
        return _error_rows(case, data, f'ground truth not found at {gt_path}', iterations)

    # Read ground truth — never modified
    df_target = pd.read_csv(gt_path, low_memory=False)
    df_target = df_target.loc[:, ~df_target.columns.str.match(r'^Unnamed')]

    def _detect_output_path(code, case_dir):
        """Detect the output CSV path from the code's to_csv() call."""
        # Look for to_csv("...") or to_csv('...') in the code
        m = _re.search(r'\.to_csv\(\s*["\']([^"\']+)["\']', code)
        if m:
            csv_path = m.group(1)
            # If it's a relative path, it should already be relative to cwd
            if os.path.isabs(csv_path):
                return csv_path
            return csv_path
        # Fallback: look for target_path = "..." variable assignment
        m = _re.search(r'target_path\s*=\s*["\']([^"\']+\.csv)["\']', code)
        if m:
            return m.group(1)
        return None

    def score_entry(entry, case, itr, source_label):
        """Score a single ms or critique entry. Returns a result dict or None on error."""
        old_score  = entry.get('score')
        is_correct = entry.get('is_correct')
        code       = entry.get('code', '')

        # Detect where this specific entry writes its output
        entry_output = _detect_output_path(code, case_dir)
        if not entry_output:
            # Fallback: ms writes to target_multisource.csv, critiques to target_multisource_critique_history.csv
            if source_label == 'ms':
                entry_output = os.path.join(case_dir, 'target_multisource.csv')
            else:
                entry_output = os.path.join(case_dir, 'target_multisource_critique_history.csv')

        # Back up existing file if present so we can restore it after exec
        backup_content = None
        if os.path.exists(entry_output):
            backup_content = open(entry_output, 'rb').read()

        local_ns   = {'__name__': '__main__'}
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exec(code, local_ns)

            if not os.path.exists(entry_output):
                print(f"[WARN] {case} iter={itr} {source_label}: code did not produce {entry_output}")
                return {
                    'case': case, 'iteration': itr, 'source': source_label,
                    'old_score': old_score, 'fd_f1': None, 'col_ratio': None,
                    'js_sim': None, 'range_overlap': None, 'wasserstein_sim': None,
                    'score_a': None, 'score_b': None, 'score_c': None,
                    'is_correct': is_correct, 'error': 'output file not produced',
                }

            df_gen = pd.read_csv(entry_output, low_memory=False)
            df_gen = df_gen.loc[:, ~df_gen.columns.str.match(r'^Unnamed')]

            fd_ratio, col_ratio, _, fd_f1, _, debug = relative_csv_score(df_gen, df_target)
            dist          = debug.get('distribution', {})
            js_sim        = dist.get('avg_js_similarity')
            wass_sim      = dist.get('avg_distribution_similarity')
            range_overlap = dist.get('avg_range_overlap')

            score_b = round((fd_f1 + col_ratio) / 2, 4)
            if js_sim is not None and range_overlap is not None:
                score_a = round((fd_f1 + col_ratio + js_sim + range_overlap) / 4, 4)
                score_c = round((fd_f1 + js_sim + range_overlap) / 3, 4)
            elif js_sim is not None:
                score_a = round((fd_f1 + col_ratio + js_sim) / 3, 4)
                score_c = round((fd_f1 + js_sim) / 2, 4)
            else:
                score_a = None
                score_c = None

            return {
                'case': case, 'iteration': itr, 'source': source_label,
                'old_score': old_score, 'fd_f1': round(fd_f1, 4),
                'col_ratio': round(col_ratio, 4), 'js_sim': js_sim,
                'range_overlap': range_overlap, 'wasserstein_sim': wass_sim,
                'score_a': score_a, 'score_b': score_b, 'score_c': score_c,
                'is_correct': is_correct, 'error': None,
            }
        except Exception as e:
            print(f"[ERROR] {case} iter={itr} {source_label}: {e}")
            return {
                'case': case, 'iteration': itr, 'source': source_label,
                'old_score': old_score, 'fd_f1': None, 'col_ratio': None,
                'js_sim': None, 'range_overlap': None, 'wasserstein_sim': None,
                'score_a': None, 'score_b': None, 'score_c': None,
                'is_correct': is_correct, 'error': str(e),
            }
        finally:
            # Restore the original file so we don't pollute the next entry's scoring
            if backup_content is not None:
                with open(entry_output, 'wb') as f:
                    f.write(backup_content)

    for it in data['iterations']:
        itr = it['iteration']
        if iterations and itr not in iterations:
            continue

        # Score ms
        row = score_entry(it['ms'], case, itr, 'ms')
        if row:
            results.append(row)

        # Score each critique
        for ci, critique in enumerate(it.get('critiques', [])):
            ctype = critique.get('type', f'critique_{ci}')
            row = score_entry(critique, case, itr, ctype)
            if row:
                results.append(row)

    return results


def main():
    parser = argparse.ArgumentParser(description='Re-score case JSONs with updated scoring formula.')
    parser.add_argument('--json_dir', required=True, help='Path to directory containing case JSONs')
    parser.add_argument('--cases', nargs='*', default=None,
                        help='Case IDs to re-score (e.g. 1_9 1_18). Omit to run all.')
    parser.add_argument('--iterations', nargs='*', type=int, default=None,
                        help='Iteration numbers to score (e.g. 1 2 3). Omit for all.')
    parser.add_argument('--output', default='rescore_results.csv', help='Output CSV path')
    args = parser.parse_args()

    json_dir = args.json_dir
    if args.cases:
        json_files = [os.path.join(json_dir, f'{c}.json') for c in args.cases]
    else:
        # Include both *.json and *.json.tmp files
        json_files = sorted(
            glob.glob(os.path.join(json_dir, '*.json')) +
            glob.glob(os.path.join(json_dir, '*.json.tmp'))
        )

    all_results = []
    for jf in json_files:
        if not os.path.exists(jf):
            print(f"[WARN] File not found: {jf}")
            continue
        print(f"Scoring {os.path.basename(jf)} ...")
        rows = rescore_json(jf, iterations=args.iterations)
        all_results.extend(rows)

    if not all_results:
        print("No results produced.")
        return

    df = pd.DataFrame(all_results)
    # Separate valid vs error rows — use valid for confusion matrices, save ALL to CSV
    valid = df[df['score_a'].notna() & df['score_b'].notna() & df['score_c'].notna() & df['old_score'].notna()]
    error_rows = df[df['score_a'].isna() | df['score_b'].isna() | df['score_c'].isna() | df['old_score'].isna()]
    n_errors = len(error_rows)
    error_cases = error_rows['case'].unique() if n_errors > 0 else []
    if n_errors > 0:
        print(f"[INFO] {n_errors} rows ({len(error_cases)} cases) had errors/missing scores — kept in CSV with error column.")
        print(f"[INFO] Error cases: {sorted(error_cases)}")
    print(f"[INFO] {len(valid)} rows ({valid['case'].nunique()} cases) scored successfully.")

    # Per-row detail table (show ALL rows including errors)
    print("\n" + "=" * 130)
    print(f"{'case':<8} {'iter':<5} {'src':<12} {'old':<8} {'score_A':<10} {'score_B':<10} {'score_C':<10} "
          f"{'fd_f1':<8} {'col_r':<8} {'js_sim':<8} {'rng_ovlp':<10} {'correct':<8} {'error'}")
    print("-" * 130)
    for _, row in df.iterrows():
        def f(v): return f"{v:.4f}" if v is not None and pd.notna(v) else "N/A"
        err = row.get('error', '')
        err_str = str(err)[:40] if err and pd.notna(err) else ''
        print(f"{row['case']:<8} {row['iteration']:<5} {row['source']:<12} {f(row['old_score']):<8} "
              f"{f(row['score_a']):<10} {f(row['score_b']):<10} {f(row['score_c']):<10} "
              f"{f(row['fd_f1']):<8} {f(row['col_ratio']):<8} {f(row['js_sim']):<8} "
              f"{f(row['range_overlap']):<10} {str(row['is_correct']):<8} {err_str}")

    # Confusion matrices for each scoring formula
    SCORES = {
        'score_A  (fd_f1 + col_ratio + js_sim + range_overlap) / 4': 'score_a',
        'score_B  (fd_f1 + col_ratio) / 2':                          'score_b',
        'score_C  (fd_f1 + js_sim + range_overlap) / 3':             'score_c',
        'old_score (stored)':                                         'old_score',
    }

    print("\n" + "=" * 60)
    print("CONFUSION MATRICES  —  score=1.0 vs is_correct")
    print("Rows = score bucket, Cols = ground-truth correctness")

    for label, col in SCORES.items():
        sub = valid[valid[col].notna() & valid['is_correct'].notna()].copy()
        if sub.empty:
            continue
        sub['score_bucket'] = sub[col].apply(lambda s: '1.0' if s == 1.0 else '<1.0')
        sub['correct_label'] = sub['is_correct'].apply(lambda c: 'True' if c else 'False')

        ct = sub.groupby(['score_bucket', 'correct_label']).size().unstack(fill_value=0)
        # Ensure both columns exist
        for c in ['True', 'False']:
            if c not in ct.columns:
                ct[c] = 0
        ct = ct[['True', 'False']]
        for r in ['1.0', '<1.0']:
            if r not in ct.index:
                ct.loc[r] = 0
        ct = ct.loc[['1.0', '<1.0']]

        tp = ct.loc['1.0', 'True']    # score=1.0, correct=True   → agreement
        tn = ct.loc['<1.0', 'False']  # score<1.0, correct=False  → agreement
        fp = ct.loc['1.0', 'False']   # score=1.0, correct=False  → disagreement (FP)
        fn = ct.loc['<1.0', 'True']   # score<1.0, correct=True   → disagreement (FN)
        total = tp + tn + fp + fn
        agreement = round(100 * (tp + tn) / total, 1) if total else 0

        # Average disagreement: treat is_correct as 1.0/0.0, compute mean |score - correctness|
        # Only on disagreeing rows so we can see how far off the score is
        correct_numeric = sub['is_correct'].apply(lambda c: 1.0 if c else 0.0)
        abs_diff = (sub[col] - correct_numeric).abs()

        fp_rows = sub[(sub[col] == 1.0) & (~sub['is_correct'])]
        fn_rows = sub[(sub[col] < 1.0)  & (sub['is_correct'])]

        fp_diff = (fp_rows[col] - 0.0).abs()   # FP: score - 0 (should be 0, got score)
        fn_diff = (1.0 - fn_rows[col]).abs()    # FN: 1 - score (should be 1, got score)

        avg_fp_gap = round(fp_diff.mean(), 4) if len(fp_diff) > 0 else 0.0
        avg_fn_gap = round(fn_diff.mean(), 4) if len(fn_diff) > 0 else 0.0
        avg_disagreement = round(abs_diff[sub['score_bucket'].ne(
            sub['correct_label'].map({'True': '1.0', 'False': '<1.0'})
        )].mean(), 4) if (fp + fn) > 0 else 0.0

        print(f"\n  {label}")
        print(f"  {'':>12} {'correct=True':>14} {'correct=False':>14}")
        print(f"  {'score=1.0':>12} {tp:>14} {fp:>14}   ← FP={fp}  avg gap={avg_fp_gap:.4f}")
        print(f"  {'score<1.0':>12} {fn:>14} {tn:>14}   ← FN={fn}  avg gap={avg_fn_gap:.4f}")
        print(f"  Agreement: {tp+tn}/{total} = {agreement}%  |  avg disagreement = {avg_disagreement:.4f}")

    # --------------------------------------------------------------------------
    # Case-level accuracy
    # For each case, iterate through iterations in order.
    # First iteration where score = 1.0:
    #   → is_correct = True  : case CORRECT
    #   → is_correct = False : case INCORRECT (stop, don't check further)
    # If no iteration reaches score = 1.0 : case INCORRECT
    # --------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("CASE-LEVEL ACCURACY")

    for label, col in SCORES.items():
        sub = valid[valid[col].notna() & valid['is_correct'].notna()].copy()
        sub = sub.sort_values(['case', 'iteration'])

        case_correct = 0
        case_incorrect = 0
        case_details = []

        for case_id, grp in sub.groupby('case'):
            verdict = None
            for _, row in grp.iterrows():
                if row[col] == 1.0:
                    verdict = 'CORRECT' if row['is_correct'] else 'INCORRECT'
                    break
            if verdict is None:
                verdict = 'INCORRECT'  # never reached 1.0

            if verdict == 'CORRECT':
                case_correct += 1
            else:
                case_incorrect += 1
            case_details.append((case_id, verdict))

        total_cases = case_correct + case_incorrect
        acc = round(100 * case_correct / total_cases, 1) if total_cases else 0

        print(f"\n  {label}")
        print(f"  Correct cases  : {case_correct}/{total_cases} = {acc}%")
        print(f"  Incorrect cases: {case_incorrect}/{total_cases}")
        print(f"  {'case':<10} {'verdict'}")
        for case_id, verdict in case_details:
            print(f"  {case_id:<10} {verdict}")

    df.to_csv(args.output, index=False)
    print(f"\nSaved: {args.output}")


if __name__ == '__main__':
    main()
