import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_10/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by PRECINCT and sum numeric columns
df_grouped = df_all.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Convert data types to match target schema
df_grouped["PRECINCT"] = df_grouped["PRECINCT"].astype(str)
df_grouped["ELIGIBLE_VOTERS"] = df_grouped["ELIGIBLE_VOTERS"].astype(int)
df_grouped["POLLS"] = df_grouped["POLLS"].astype(int)
df_grouped["EARLY_VOING"] = df_grouped["EARLY_VOING"].astype(int)
df_grouped["ABSENTEE"] = df_grouped["ABSENTEE"].astype(int)
df_grouped["PROVISIONAL"] = df_grouped["PROVISIONAL"].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)