"""
cluster_cases_by_value_graph.py
==================================
Clusters L1+L4+L9 cases together (minus the 7 outlier cases identified in the
name-similarity clustering attempt) using the ORIGINAL value-based graph
structure from code_archive/GraphCreation.ipynb, but with node features
actually wired into the embedding (the original notebook computed rich
per-column features yet called Graph2Vec() with use_node_attribute=None,
silently discarding them — this version fixes that).

Graph per case:
  - Nodes = every column (target.csv + all test_N.csv sources), each carrying
    a `feature_tuple` attribute: (uniqueness_ratio [binned to 1 decimal],
    dtype_code, is_target).
  - Edges = value-based, exactly as in GraphCreation.ipynb: for column pairs
    from DIFFERENT tables with the same dtype, an edge exists if
    jaccard_similarity >= 0.9 OR jaccard_containment >= 0.9, computed on a
    500-row sample of each table (not the full table) for both column
    feature computation and Jaccard matching.

Graph2Vec is then run with use_node_attribute="feature_tuple" so the WL
hashing actually incorporates these 3 features, not just node degree.
KMeans(n_clusters=5) on the standardized embeddings, matching prior runs.

Usage: python3 cluster_cases_by_value_graph.py
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import os
import glob
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

from model.join.data import jaccard_similarity, jaccard_containment

BASE_DIR = "autopipeline-benchmarks/github-pipelines"
LENGTHS = [1, 4, 9]
N_CLUSTERS = 5
SIM_THRESHOLD = 0.9
SAMPLE_N = 500
SEED = 42
MAX_SOURCE_TABLES = 20  # a few L9 mega-cases have 136-223 source tables vs a
                         # median of 5; cap so their graphs stay comparable in
                         # scale to the rest instead of being excluded outright

# Outlier cases from the name-similarity clustering attempt that fell into
# tiny degenerate clusters (2/3/4 cases each) — excluded here too.
EXCLUDE_CASES = {
    "length4_62", "length4_63", "length4_64", "length4_87",
    "length9_78", "length9_79", "length9_96",
}

DTYPE_CODE = {"int64": 0, "float64": 1, "object": 2, "bool": 3}


def sample_rows(df: pd.DataFrame, n: int = SAMPLE_N, seed: int = SEED) -> pd.DataFrame:
    return df.sample(n, random_state=seed) if len(df) > n else df


def read_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df = df.drop(df.columns[0], axis=1)  # drop index column, matches nodes.py convention
    return sample_rows(df)


def get_column_names(csv_path: str):
    try:
        df = pd.read_csv(csv_path, nrows=0, low_memory=False)
        return [c for c in df.columns if not c.startswith("Unnamed")]
    except Exception:
        return []


def column_features(col: pd.Series, is_target: bool):
    uniqueness_ratio = round(col.nunique(dropna=True) / max(len(col), 1), 1)  # binned to 1 decimal
    dtype_code = DTYPE_CODE.get(str(col.dtype), -1)
    return (uniqueness_ratio, dtype_code, int(is_target))


def build_case_graph(case_dir: str):
    target_path = os.path.join(case_dir, "target.csv")
    source_paths = sorted(glob.glob(os.path.join(case_dir, "test_*.csv")))[:MAX_SOURCE_TABLES]
    if not os.path.exists(target_path) or not source_paths:
        return None

    tables = {"target": read_table(target_path)}
    for i, sp in enumerate(source_paths):
        tables[f"source_{i}"] = read_table(sp)
    tables = {k: v for k, v in tables.items() if v.shape[1] > 0}
    if len(tables) < 2:
        return None

    G = nx.Graph()
    node_id = {}
    nid = 0
    for table_name, tbl in tables.items():
        is_target = table_name == "target"
        for col in tbl.columns:
            try:
                feat = column_features(tbl[col], is_target)
            except Exception:
                feat = (0.0, -1, int(is_target))
            node_id[(table_name, col)] = nid
            G.add_node(nid, feature_tuple=feat)
            nid += 1

    for t1, t2 in combinations(tables.keys(), 2):
        tbl1, tbl2 = tables[t1], tables[t2]
        for c1 in tbl1.columns:
            for c2 in tbl2.columns:
                if tbl1[c1].dtype != tbl2[c2].dtype:
                    continue
                try:
                    js = jaccard_similarity(tbl1[c1], tbl2[c2])
                    jc = jaccard_containment(tbl1[c1], tbl2[c2])
                    if js >= SIM_THRESHOLD or jc >= SIM_THRESHOLD:
                        G.add_edge(node_id[(t1, c1)], node_id[(t2, c2)])
                except Exception:
                    pass

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
                print(f"  skip {case_name}: could not build graph")
                continue
            fg_map[case_name] = G

    print(f"Built {len(fg_map)} graphs across L{LENGTHS}")

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

    graph2vec = Graph2Vec(use_node_attribute="feature_tuple")
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
    df.to_csv("value_graph_clusters.csv", index=False)
    print("\nSaved cluster assignments -> value_graph_clusters.csv")

    print(f"\n{'='*60}\nCluster sizes\n{'='*60}")
    print(df["cluster"].value_counts().sort_index())

    print(f"\n{'='*60}\nCluster composition by length\n{'='*60}")
    print(pd.crosstab(df["cluster"], df["length"]))

    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embedding_scaled)
    plt.figure(figsize=(8, 6))
    for length, marker in zip(LENGTHS, ["o", "s", "^"]):
        mask = df["length"] == str(length)
        plt.scatter(reduced[mask.values, 0], reduced[mask.values, 1],
                    c=df.loc[mask, "cluster"], cmap="tab10", marker=marker,
                    label=f"L{length}", edgecolors="black", s=60)
    plt.legend()
    plt.title("Case clusters (value-Jaccard graph + node features), L1+L4+L9 combined")
    plt.savefig("value_graph_clusters.png", dpi=150, bbox_inches="tight")
    print("Saved plot -> value_graph_clusters.png")


if __name__ == "__main__":
    main()
