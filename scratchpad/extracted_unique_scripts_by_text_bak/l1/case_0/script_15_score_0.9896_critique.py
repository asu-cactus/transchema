import pandas as pd

# List all source files (assuming 3 source files as an example)
file_paths = [
    "autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_0/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_0/training_2.csv"
]

# Read and union all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df = pd.concat(dfs, ignore_index=True)

# Strip whitespace from "State" column
df["State"] = df["State"].str.strip()

# Group by State and compute mean AverageTemperature
result = df.groupby("State", as_index=False)["AverageTemperature"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)