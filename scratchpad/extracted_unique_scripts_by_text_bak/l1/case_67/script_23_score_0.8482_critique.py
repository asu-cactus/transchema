import pandas as pd

# Read the single source file
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_67/training_0.csv", index_col=0)

# Rename columns to match target schema
df = source0.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})

# Select relevant columns
df = df[["user_id", "sad", "stressed"]]

# Ensure correct types
df["user_id"] = df["user_id"].astype(int)
df["sad"] = df["sad"].astype(float)
df["stressed"] = df["stressed"].astype(float)

# Group by user_id and aggregate by mean
result = df.groupby("user_id", as_index=False).agg({"sad": "mean", "stressed": "mean"})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts.csv", index=False)