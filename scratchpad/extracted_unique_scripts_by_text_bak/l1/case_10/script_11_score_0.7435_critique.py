import pandas as pd
import glob

# Read all source files matching the pattern (assuming multiple source files exist)
# The problem only explicitly shows Source1_10_0, but instructions say all source tables must be used.
# So we glob all files starting with training_*.csv in the directory.

file_pattern = "autopipeline-benchmarks/github-pipelines/length1_10/training_*.csv"
files = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by PRECINCT and sum the numeric columns
agg = df_all.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Cast columns to correct types as per target schema
agg["PRECINCT"] = agg["PRECINCT"].astype(str)
agg["ELIGIBLE_VOTERS"] = agg["ELIGIBLE_VOTERS"].astype(int)
agg["POLLS"] = agg["POLLS"].astype(int)
agg["EARLY_VOING"] = agg["EARLY_VOING"].astype(int)
agg["ABSENTEE"] = agg["ABSENTEE"].astype(int)
agg["PROVISIONAL"] = agg["PROVISIONAL"].astype(int)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)