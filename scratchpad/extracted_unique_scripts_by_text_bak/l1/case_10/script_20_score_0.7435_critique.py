import pandas as pd

# List all source files (assuming 10 source files named training_0.csv to training_9.csv)
source_files = [
    f"autopipeline-benchmarks/github-pipelines/length1_10/training_{i}.csv" for i in range(10)
]

# Read and concatenate all source tables (union)
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df = pd.concat(dfs, ignore_index=True)

# Group by PRECINCT and sum numeric columns
df = df.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Cast columns to correct types as per target schema
df["PRECINCT"] = df["PRECINCT"].astype(str)
df["ELIGIBLE_VOTERS"] = df["ELIGIBLE_VOTERS"].astype(int)
df["POLLS"] = df["POLLS"].astype(int)
df["EARLY_VOING"] = df["EARLY_VOING"].astype(int)
df["ABSENTEE"] = df["ABSENTEE"].astype(int)
df["PROVISIONAL"] = df["PROVISIONAL"].astype(int)

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)