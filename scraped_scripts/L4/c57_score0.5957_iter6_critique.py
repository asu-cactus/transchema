import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

# Union all source tables
result = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Drop rows where TransTo is NaN (if any)
result = result.dropna(subset=["TransTo"])

# Convert columns to integer type as per target schema
result["TransTo"] = result["TransTo"].astype(int)
result["WarNum"] = result["WarNum"].astype(int)

# Reorder columns to match target schema: ['TransTo', 'WarNum']
result = result[["TransTo", "WarNum"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)