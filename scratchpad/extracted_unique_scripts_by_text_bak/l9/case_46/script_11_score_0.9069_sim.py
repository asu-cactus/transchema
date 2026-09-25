import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_46/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_46/training_14.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

counts = []
for df in dfs:
    count_df = df.groupby("purpose").size().reset_index(name="count")
    counts.append(count_df)

from functools import reduce

def merge_counts(left, right):
    return pd.merge(left, right, on="purpose", how="outer", suffixes=('', '_y'))

merged = reduce(merge_counts, counts)

count_cols = [col for col in merged.columns if col != "purpose"]

merged["purpose"] = merged["purpose"].astype(int)

merged["count"] = merged[count_cols].fillna(0).sum(axis=1).astype(int)

result = merged[["purpose", "count"]].rename(columns={"count": "purpose"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_46/target_multisource_mcts.csv", index=False)