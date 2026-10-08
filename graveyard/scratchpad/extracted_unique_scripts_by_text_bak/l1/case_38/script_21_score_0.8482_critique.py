import pandas as pd

# List all source files
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_38/training_4.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by user_id and aggregate mean of sad.depressed and open.stressed
agg = df_all.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

# Rename columns to match target schema
agg = agg.rename(columns={"sad.depressed": "sad", "open.stressed": "stressed"})

# Ensure correct types
agg["user_id"] = agg["user_id"].astype(int)
agg["sad"] = agg["sad"].astype(float)
agg["stressed"] = agg["stressed"].astype(float)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)