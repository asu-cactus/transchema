"""
fuzzy_match: partial-credit variant of compare_tables from autopipeline_match.

Identical logic to compare_tables except:
  1. Row-length mismatch does NOT abort — matching continues on all columns.
  2. A target column with no match does NOT abort — it is skipped (counts as 0).
  3. Returns (score, matched_cols) where score = matched / total_target_columns,
     instead of (True/False, matched_cols).
"""

import pandas as pd
from validation.autopipeline_match import compare_series, compare_dfs


def compare_tables_fuzzy(df_generate, df_target):
    total = len(df_target.columns)
    if total == 0:
        return 0.0, []

    # compare length firstly
    if len(df_generate) != len(df_target):
        print("THEY ARE OF DIFFERNET LENGTH: ", len(df_generate), len(df_target))
    else:
        print("THEY ARE OF SAME LENGTH: ", len(df_generate), len(df_target))
    col_map = {}
    map_num = 1
    one_map = {}
    mul_map = {}
    results = []
    for col_target in df_target.columns:
        col_map[col_target] = []
        col_target_data = df_target[col_target]
        for col_generate in df_generate.columns:
            col_generate_data = df_generate[col_generate]
            # compare the data
            if compare_series(col_target_data, col_generate_data):
                col_map[col_target].append(col_generate)
                results.append(col_generate)
                break
        # can't find correspond columns, skip instead of returning False
        if len(col_map[col_target]) == 0:
            print("didn't find corresponding columns for {}".format(col_target))
            continue
        map_num = map_num * len(col_map[col_target])
        # split them to two maps, one contain columns which only has one mapped column, mul contains columsn which has multiple mapped columns
        if len(col_map[col_target]) == 1:
            one_map[col_target] = col_map[col_target]
        else:
            mul_map[col_target] = col_map[col_target]
    print("map_num = {}".format(map_num), "MATCHED")
    if map_num >= 1:
        score = len(results) / total
        print(f"[fuzzy_match] Matched {len(results)}/{total} columns → score={score:.4f}")
        return score, results
    basic_target = pd.DataFrame()
    basic_generate = pd.DataFrame()
    for col_target, col_maps in one_map.items():
        col_map = col_maps[0]
        basic_target[col_target] = df_target[col_target]
        basic_generate[col_target] = df_generate[col_map]
        results.append(col_map)
    if map_num == 1:
        try:
            if [
                s
                for s in (basic_generate == df_generate).sum()
                if s == len(basic_generate)
            ] == len(basic_generate.columns):
                score = len(results) / total
                print(f"[fuzzy_match] Matched {len(results)}/{total} columns → score={score:.4f}")
                return score, results
        except:
            pass
    # first compare the columns with only 1 map and greedy add the one with multiple choices
    if not compare_dfs(basic_target, basic_generate):
        # basic is different, return false
        return False, []
    for col_target, col_maps in mul_map.items():
        for col_map in col_maps:
            basic_target[col_target] = df_target[col_target]
            basic_generate[col_target] = df_generate[col_map]
            if compare_dfs(basic_target, basic_generate):
                results.append(col_map)
                continue
            else:
                # this column doesn't match, drop it and test another one
                basic_target.drop(col_target, axis=1)
                basic_generate.drop(col_target, axis=1)
        # if none of the candidates in the mapped columns work, return False
        if col_target not in basic_target.columns:
            return False, []
    score = len(results) / total
    print(f"[fuzzy_match] Matched {len(results)}/{total} columns → score={score:.4f}")
    return score, results


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    def run_test(name, df_gen, df_tgt, expected_score):
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        score, matched = compare_tables_fuzzy(df_gen, df_tgt)
        status = "PASS" if abs(score - expected_score) < 1e-6 else "FAIL"
        print(f"  score={score:.4f}  matched={matched}  expected={expected_score:.4f}  [{status}]")
        return status == "PASS"

    results = []

    # ── Test 1: Perfect match — all 3 columns align ───────────────────────────
    gen = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35], "city": ["NY", "LA", "SF"]})
    tgt = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35], "city": ["NY", "LA", "SF"]})
    results.append(run_test("Perfect match (3/3)", gen, tgt, expected_score=1.0))

    # ── Test 2: Partial match — 2 of 4 target columns found in generated ──────
    gen = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35]})
    tgt = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35], "city": ["NY", "LA", "SF"], "score": [0.9, 0.7, 0.8]})
    results.append(run_test("Partial match (2/4)", gen, tgt, expected_score=0.5))

    # ── Test 3: No columns match ──────────────────────────────────────────────
    gen = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    tgt = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35]})
    results.append(run_test("No match (0/2)", gen, tgt, expected_score=0.0))

    # ── Test 4: Row-length mismatch but columns still match ───────────────────
    # compare_tables would abort here; fuzzy should still find matching columns
    gen = pd.DataFrame({"name": ["alice", "bob"], "age": [30, 25]})
    tgt = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35]})
    # compare_series checks length after dropna, so these won't match — score=0
    results.append(run_test("Row mismatch — no match expected (0/2)", gen, tgt, expected_score=0.0))

    # ── Test 5: Column names differ but data matches (renamed column) ─────────
    gen = pd.DataFrame({"full_name": ["alice", "bob", "carol"], "years": [30, 25, 35]})
    tgt = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35]})
    results.append(run_test("Renamed columns — data still matches (2/2)", gen, tgt, expected_score=1.0))

    # ── Test 6: 1 of 3 columns matches ───────────────────────────────────────
    gen = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [99, 99, 99], "city": ["X", "Y", "Z"]})
    tgt = pd.DataFrame({"name": ["alice", "bob", "carol"], "age": [30, 25, 35], "city": ["NY", "LA", "SF"]})
    results.append(run_test("1 of 3 columns match (1/3)", gen, tgt, expected_score=1/3))

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    passed = sum(results)
    print(f"SUMMARY: {passed}/{len(results)} tests passed")
    print(f"{'='*60}")
