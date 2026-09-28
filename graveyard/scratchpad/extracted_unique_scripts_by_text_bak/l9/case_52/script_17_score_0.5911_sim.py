import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_52/training_14.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

counts = []
for df in dfs:
    counts.append(df.groupby("zip_code").size().rename("count"))

agg_df = pd.concat(counts, axis=1).fillna(0)
agg_df["total_count"] = agg_df.sum(axis=1)
result = agg_df[["total_count"]].reset_index()
result.columns = ["zip_code", "count"]
result["zip_code"] = result["zip_code"].astype(int)
result["count"] = result["count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts.csv", index=False)