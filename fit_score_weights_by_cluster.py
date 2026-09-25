"""
fit_score_weights_by_cluster.py
==================================
Checks whether fitting SEPARATE score_1 weights per operator-cluster (from
cluster_cases_by_operator_freq.py's operator_freq_clusters.csv: cluster 0 =
merge/join-style pipelines, cluster 1 = concat/union-style pipelines) beats
a single global weight vector fit across all cases.

For each cluster with enough cases (0 and 1; clusters 2/3/4 have only 5/2/1
cases each -- too small to fit or meaningfully evaluate), splits that
cluster's cases 80/20, fits pairwise ranking logistic regression
(fit_pairwise, same method as fit_score_weights_regression.py) on the
cluster's own train split, and compares three things on the SAME held-out
cluster cases:
  - Equal-weight baseline (current formula)
  - GLOBAL pairwise-LR weights (fit on ALL 273 cases, ignoring cluster)
  - CLUSTER-SPECIFIC pairwise-LR weights (fit only on this cluster's cases)

Usage: python3 fit_score_weights_by_cluster.py [--cluster_file value_graph_clusters.csv]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import argparse
import random
import numpy as np
import pandas as pd

from fit_score_weights_regression import (
    load_clean_rows, group_by_case, fit_pairwise, eval_weights, FEATURES,
)

SEED = 42
MIN_CLUSTER_SIZE = 20


def load_cluster_map(path="operator_freq_clusters.csv"):
    df = pd.read_csv(path)
    length = df["case"].str.extract(r"length(\d+)_")[0]
    case_num = df["case"].str.extract(r"_(\d+)$")[0]
    return {(l, c): cl for l, c, cl in zip(length, case_num, df["cluster"])}


def split_within(case_keys, test_frac=0.2, seed=SEED):
    keys = sorted(case_keys)
    rng = random.Random(seed)
    rng.shuffle(keys)
    n_test = max(1, int(len(keys) * test_frac))
    test_keys = set(keys[:n_test])
    train_keys = set(keys) - test_keys
    return train_keys, test_keys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster_file", default="operator_freq_clusters.csv")
    args = parser.parse_args()

    rows = load_clean_rows()
    cluster_map = load_cluster_map(args.cluster_file)
    for r in rows:
        r["_cluster"] = cluster_map.get((r["length"], r["case_num"]))
    rows = [r for r in rows if r["_cluster"] is not None]

    groups_all = group_by_case(rows)
    equal_w = np.array([0.25, 0.25, 0.25, 0.25])

    # Global pairwise-LR, fit on ALL cases regardless of cluster (from earlier analysis)
    global_w = fit_pairwise(groups_all)
    print("Global pairwise-LR weights (all clusters combined):",
          dict(zip(FEATURES, np.round(global_w, 4))))

    cluster_sizes = pd.Series([r["_cluster"] for r in rows]).value_counts().sort_index()
    print(f"\nCluster sizes (rows): {dict(cluster_sizes)}")
    case_counts = {}
    for r in rows:
        case_counts.setdefault(r["_cluster"], set()).add((r["length"], r["case_num"]))
    print(f"Cluster sizes (cases): {{k: len(v) for k, v in case_counts.items()}}"
          .replace("{k: len(v) for k, v in case_counts.items()}",
                   str({k: len(v) for k, v in case_counts.items()})))

    for cluster_id, case_keys in sorted(case_counts.items()):
        if len(case_keys) < MIN_CLUSTER_SIZE:
            print(f"\n{'='*70}\nCluster {cluster_id}: only {len(case_keys)} cases — "
                  f"too small to fit/evaluate separately (min {MIN_CLUSTER_SIZE}), skipping.\n{'='*70}")
            continue

        train_keys, test_keys = split_within(case_keys)
        cluster_groups = {k: v for k, v in groups_all.items() if k in case_keys}
        train_groups = {k: v for k, v in cluster_groups.items() if k in train_keys}

        cluster_w = fit_pairwise(train_groups)

        print(f"\n{'='*70}\nCluster {cluster_id} ({len(case_keys)} cases: "
              f"{len(train_keys)} train / {len(test_keys)} test)\n{'='*70}")
        print("Cluster-specific pairwise-LR weights:",
              dict(zip(FEATURES, np.round(cluster_w, 4))))

        print(f"\n{'Method':<32}{'Held-out (this cluster)':<28}{'Train (this cluster, in-sample)':<32}")
        for name, w in [("Equal-weight (baseline)", equal_w),
                        ("Global pairwise-LR", global_w),
                        ("Cluster-specific pairwise-LR", cluster_w)]:
            n_ok_test, n_test, _ = eval_weights(w, cluster_groups, test_keys)
            n_ok_train, n_train, _ = eval_weights(w, cluster_groups, train_keys)
            test_str = f"{n_ok_test}/{n_test} ({100*n_ok_test/n_test:.1f}%)"
            train_str = f"{n_ok_train}/{n_train} ({100*n_ok_train/n_train:.1f}%)"
            print(f"{name:<32}{test_str:<28}{train_str:<32}")

    # Small clusters: just report baseline (not enough data to fit anything)
    small = {k: v for k, v in case_counts.items() if len(v) < MIN_CLUSTER_SIZE}
    if small:
        all_small_keys = set().union(*small.values())
        small_groups = {k: v for k, v in groups_all.items() if k in all_small_keys}
        print(f"\n{'='*70}\nSmall clusters combined ({', '.join(str(k) for k in small)}) "
              f"— {len(all_small_keys)} cases, baseline only\n{'='*70}")
        for name, w in [("Equal-weight (baseline)", equal_w),
                        ("Global pairwise-LR", global_w)]:
            n_ok, n_total, _ = eval_weights(w, small_groups, all_small_keys)
            print(f"{name:<32}{n_ok}/{n_total} ({100*n_ok/n_total:.1f}%)")

    # Overall: cluster-specific weights applied to their own cluster's held-out
    # cases, combined, vs. global weights on the same combined held-out set.
    print(f"\n{'='*70}\nOVERALL: held-out accuracy, global weights vs. per-cluster weights\n{'='*70}")
    total_global_ok = total_specific_ok = total_baseline_ok = total_n = 0
    for cluster_id, case_keys in sorted(case_counts.items()):
        if len(case_keys) < MIN_CLUSTER_SIZE:
            continue
        train_keys, test_keys = split_within(case_keys)
        cluster_groups = {k: v for k, v in groups_all.items() if k in case_keys}
        train_groups = {k: v for k, v in cluster_groups.items() if k in train_keys}
        cluster_w = fit_pairwise(train_groups)

        ok_b, n, _ = eval_weights(equal_w, cluster_groups, test_keys)
        ok_g, _, _ = eval_weights(global_w, cluster_groups, test_keys)
        ok_s, _, _ = eval_weights(cluster_w, cluster_groups, test_keys)
        total_baseline_ok += ok_b
        total_global_ok += ok_g
        total_specific_ok += ok_s
        total_n += n

    print(f"Equal-weight (baseline):        {total_baseline_ok}/{total_n} ({100*total_baseline_ok/total_n:.1f}%)")
    print(f"Global pairwise-LR:              {total_global_ok}/{total_n} ({100*total_global_ok/total_n:.1f}%)")
    print(f"Cluster-specific pairwise-LR:    {total_specific_ok}/{total_n} ({100*total_specific_ok/total_n:.1f}%)")


if __name__ == "__main__":
    main()
