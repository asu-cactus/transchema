"""
cluster_cases_by_name_graph.py
=================================
Clusters L1+L4+L9 cases together by schema structure, using a per-case graph
whose nodes are columns (across target.csv + all test_N.csv source tables)
and whose edges connect columns with SIMILAR NAMES across different tables
(not similar values, unlike code_archive/GraphCreation.ipynb):

  edge(col_a, col_b)  iff  difflib.SequenceMatcher(name_a, name_b).ratio() >= 0.8
                       OR   longest_common_prefix(name_a, name_b) >= 3
                       OR   longest_common_suffix(name_a, name_b) >= 3

(names lowercased before comparing; edges only between columns from different
tables within the same case, mirroring GraphCreation.ipynb's structure).

Each case's graph is embedded with karateclub's Graph2Vec (same as
GraphCreation.ipynb: dimensions=128, structural WL features only — no node
attributes are attached/used), then all L1+L4+L9 embeddings are standardized
and clustered together with KMeans(n_clusters=5).

Usage: python3 cluster_cases_by_name_graph.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import os
import glob
import difflib
import numpy as np
import pandas as pd
import networkx as nx
from itertools import combinations
from karateclub import Graph2Vec
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = "autopipeline-benchmarks/github-pipelines"
LENGTHS = [1, 4, 9]
N_CLUSTERS = 5
SIM_THRESHOLD = 0.8
AFFIX_THRESHOLD = 3

# Outlier cases from the first run that fell into tiny degenerate clusters
# (2/3/4 cases each) — excluded here so they don't distort the embedding for
# the remaining, better-populated cases.
EXCLUDE_CASES = {
    "length4_62", "length4_63", "length4_64", "length4_87",
    "length9_78", "length9_79", "length9_96",
}


def get_column_names(csv_path):
    try:
        df = pd.read_csv(csv_path, nrows=0, low_memory=False)
        return [c for c in df.columns if not c.startswith("Unnamed")]
    except Exception:
        return []


def names_similar(a: str, b: str) -> bool:
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return True
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if ratio >= SIM_THRESHOLD:
        return True
    max_prefix = 0
    for x, y in zip(a, b):
        if x != y:
            break
        max_prefix += 1
    if max_prefix >= AFFIX_THRESHOLD:
        return True
    max_suffix = 0
    for x, y in zip(reversed(a), reversed(b)):
        if x != y:
            break
        max_suffix += 1
    if max_suffix >= AFFIX_THRESHOLD:
        return True
    return False


def build_case_graph(case_dir: str):
    """Build the name-similarity column graph for one case directory."""
    target_path = os.path.join(case_dir, "target.csv")
    source_paths = sorted(glob.glob(os.path.join(case_dir, "test_*.csv")))
    if not os.path.exists(target_path) or not source_paths:
        return None

    tables = {"target": get_column_names(target_path)}
    for i, sp in enumerate(source_paths):
        tables[f"source_{i}"] = get_column_names(sp)
    tables = {k: v for k, v in tables.items() if v}
    if len(tables) < 2:
        return None

    G = nx.Graph()
    node_id = {}
    nid = 0
    for table_name, cols in tables.items():
        for col in cols:
            node_id[(table_name, col)] = nid
            G.add_node(nid, table_name=table_name)
            nid += 1

    for t1, t2 in combinations(tables.keys(), 2):
        for c1 in tables[t1]:
            for c2 in tables[t2]:
                if names_similar(c1, c2):
                    G.add_edge(node_id[(t1, c1)], node_id[(t2, c2)])

    if G.number_of_nodes() == 0:
        return None
    return G


def main():
    fg_map = {}
    for length in LENGTHS:
        case_dirs = sorted(glob.glob(os.path.join(BASE_DIR, f"length{length}_*")))
        for case_dir in case_dirs:
            case_name = os.path.basename(case_dir)
            if case_name in EXCLUDE_CASES:
                continue
            G = build_case_graph(case_dir)
            if G is None:
                print(f"  skip {case_name}: could not build graph (missing/empty tables)")
                continue
            fg_map[case_name] = G

    print(f"Built {len(fg_map)} graphs across L{LENGTHS}")

    # Sanity filter, mirrors GraphCreation.ipynb cell 6: node IDs must be a clean 0..n-1 range.
    problematic = [name for name, G in fg_map.items()
                   if sorted(G.nodes()) != list(range(G.number_of_nodes()))]
    for name in problematic:
        del fg_map[name]
    if problematic:
        print(f"Dropped {len(problematic)} malformed graphs: {problematic}")

    case_names = list(fg_map.keys())
    g_list = list(fg_map.values())
    print(f"{len(g_list)} graphs going into Graph2Vec")
    print(f"  avg nodes={np.mean([G.number_of_nodes() for G in g_list]):.1f}  "
          f"avg edges={np.mean([G.number_of_edges() for G in g_list]):.1f}")

    graph2vec = Graph2Vec()
    graph2vec.fit(g_list)
    embedding = graph2vec.get_embedding()
    print(f"Embedding shape: {embedding.shape}")

    scaler = StandardScaler()
    embedding_scaled = scaler.fit_transform(embedding)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    cluster_ids = kmeans.fit_predict(embedding_scaled)

    def parse_length(case_name):
        return case_name.split("_")[0].replace("length", "")

    df = pd.DataFrame({
        "case": case_names,
        "length": [parse_length(c) for c in case_names],
        "cluster": cluster_ids,
    })
    df.to_csv("name_graph_clusters.csv", index=False)
    print("\nSaved cluster assignments -> name_graph_clusters.csv")

    print(f"\n{'='*60}\nCluster sizes\n{'='*60}")
    print(df["cluster"].value_counts().sort_index())

    print(f"\n{'='*60}\nCluster composition by length\n{'='*60}")
    print(pd.crosstab(df["cluster"], df["length"]))

    # 2D PCA visualization
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embedding_scaled)
    plt.figure(figsize=(8, 6))
    for length, marker in zip(LENGTHS, ["o", "s", "^"]):
        mask = df["length"] == str(length)
        plt.scatter(reduced[mask.values, 0], reduced[mask.values, 1],
                    c=df.loc[mask, "cluster"], cmap="tab10", marker=marker,
                    label=f"L{length}", edgecolors="black", s=60)
    plt.legend()
    plt.title("Case clusters (name-similarity graph + Graph2Vec), L1+L4+L9 combined")
    plt.savefig("name_graph_clusters.png", dpi=150, bbox_inches="tight")
    print("Saved plot -> name_graph_clusters.png")


if __name__ == "__main__":
    main()
