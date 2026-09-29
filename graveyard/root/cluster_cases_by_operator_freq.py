"""
cluster_cases_by_operator_freq.py
====================================
Clusters L1+L4+L9 cases together by the GROUND-TRUTH operator sequence that
generated each case (ground_truth_pipelines.csv), rather than by schema
structure. Two normalization steps applied to the raw operator list before
building frequency vectors:

1. Alias merge: 'union' and 'cat' are the same operation as 'concat' (both
   'union' and 'cat' get relabeled to 'concat' — 'cat' only ever appears
   immediately after a run of 'union's, e.g. ['union']*8 + ['cat'], and is
   clearly shorthand for the same concatenation step).
2. Collapse consecutive runs of the same (post-alias) operator into a single
   occurrence, e.g. ['concat']*221 -> ['concat'] -> concat count of 1, not
   221; ['merge','merge','merge','groupby'] -> ['merge','groupby'] -> merge=1,
   groupby=1. This avoids a handful of extreme-length L9 cases (up to 221 raw
   ops, almost all repeated concat/union) from dominating the clustering
   purely on scale rather than on the actual operator MIX used.

Vocabulary after normalization: concat, groupby, lower, merge, pivot, split,
unpivot, Date.

Standardizes the frequency vectors and clusters with KMeans(n_clusters=5),
matching the graph-based clustering for comparability.

Usage: python3 cluster_cases_by_operator_freq.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import ast
import re
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LENGTHS = [1, 4, 9]
N_CLUSTERS = 5


def parse_target_id(tid: str):
    m = re.match(r"Target(\d+)_(\d+)", tid)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


OPERATOR_ALIASES = {
    "union": "concat",
    "cat": "concat",
}


def collapse_consecutive(ops: list) -> list:
    """Collapse consecutive runs of the same operator into a single occurrence."""
    collapsed = []
    for op in ops:
        if not collapsed or collapsed[-1] != op:
            collapsed.append(op)
    return collapsed


def main():
    df = pd.read_csv("ground_truth_pipelines.csv")
    df = df[df["pipeline_length"].isin(LENGTHS)].copy()
    df["length"], df["case_num"] = zip(*df["target_id"].map(parse_target_id))
    df["case"] = df.apply(lambda r: f"length{r['length']}_{r['case_num']}", axis=1)
    df["op_list_raw"] = df["operators"].apply(ast.literal_eval)
    df["op_list_aliased"] = df["op_list_raw"].apply(
        lambda ops: [OPERATOR_ALIASES.get(op, op) for op in ops]
    )
    df["op_list"] = df["op_list_aliased"].apply(collapse_consecutive)

    vocab = sorted({op for ops in df["op_list"] for op in ops})
    print(f"{len(df)} cases across lengths {LENGTHS}")
    print(f"Operator vocabulary ({len(vocab)}): {vocab}")

    def freq_vector(ops):
        counts = pd.Series(ops).value_counts()
        return [int(counts.get(op, 0)) for op in vocab]

    feat = np.stack(df["op_list"].apply(freq_vector).values)
    feat_df = pd.DataFrame(feat, columns=vocab)
    feat_df.insert(0, "case", df["case"].values)
    feat_df.insert(1, "length", df["length"].values)
    feat_df.insert(2, "pipeline_len_raw", df["op_list_raw"].apply(len).values)
    feat_df.insert(3, "pipeline_len_collapsed", df["op_list"].apply(len).values)

    scaler = StandardScaler()
    feat_scaled = scaler.fit_transform(feat)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    cluster_ids = kmeans.fit_predict(feat_scaled)
    feat_df["cluster"] = cluster_ids

    feat_df.to_csv("operator_freq_clusters.csv", index=False)
    print("\nSaved cluster assignments -> operator_freq_clusters.csv")

    print(f"\n{'='*60}\nCluster sizes\n{'='*60}")
    print(feat_df["cluster"].value_counts().sort_index())

    print(f"\n{'='*60}\nCluster composition by length\n{'='*60}")
    print(pd.crosstab(feat_df["cluster"], feat_df["length"]))

    print(f"\n{'='*60}\nCluster profile — mean operator frequency per cluster\n{'='*60}")
    profile = feat_df.groupby("cluster")[vocab + ["pipeline_len_raw", "pipeline_len_collapsed"]].mean().round(2)
    print(profile)

    # 2D PCA visualization
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(feat_scaled)
    plt.figure(figsize=(8, 6))
    for length, marker in zip(LENGTHS, ["o", "s", "^"]):
        mask = feat_df["length"] == length
        plt.scatter(reduced[mask.values, 0], reduced[mask.values, 1],
                    c=feat_df.loc[mask, "cluster"], cmap="tab10", marker=marker,
                    label=f"L{length}", edgecolors="black", s=60)
    plt.legend()
    plt.title("Case clusters (ground-truth operator frequency), L1+L4+L9 combined")
    plt.savefig("operator_freq_clusters.png", dpi=150, bbox_inches="tight")
    print("Saved plot -> operator_freq_clusters.png")


if __name__ == "__main__":
    main()
