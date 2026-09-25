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

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all dataframes (concatenate vertically)
union_df = pd.concat(dfs, ignore_index=True)

# GROUP BY 'purpose' and count occurrences
result = union_df.groupby("purpose").size().reset_index(name="purpose")

# Ensure 'purpose' column is integer type as in target schema
result["purpose"] = result["purpose"].astype(int)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_46/target_multisource_mcts.csv", index=False)