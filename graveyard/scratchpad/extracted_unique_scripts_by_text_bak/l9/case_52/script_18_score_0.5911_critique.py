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

# UNION all source tables by concatenation
union_df = pd.concat(dfs, ignore_index=True)

# GROUP BY zip_code and count occurrences
result = union_df.groupby("zip_code").size().reset_index(name="count")

# Ensure correct types
result["zip_code"] = result["zip_code"].astype(int)
result["count"] = result["count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts.csv", index=False)