import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_57/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

counts = []
for df in dfs:
    counts.append(df.groupby("last_credit_pull_d").size())

agg_df = pd.concat(counts, axis=1).fillna(0)
agg_df.columns = [f"count_{i}" for i in range(len(dfs))]
agg_df["last_credit_pull_d"] = agg_df.index
agg_df["total_count"] = agg_df.sum(axis=1)
result = agg_df[["last_credit_pull_d", "total_count"]].copy()
result = result.rename(columns={"total_count": "last_credit_pull_d"})
result = result.reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_57/target_multisource_mcts.csv", index=False)