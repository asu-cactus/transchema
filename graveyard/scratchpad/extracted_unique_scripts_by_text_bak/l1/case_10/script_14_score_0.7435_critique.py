import pandas as pd
import glob

# Read all source files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_10/training_*.csv"
file_list = sorted(glob.glob(file_pattern))

# Read and concatenate all source tables
df_list = [pd.read_csv(f, index_col=0) for f in file_list]
df_all = pd.concat(df_list, ignore_index=True)

# Group by PRECINCT and sum the numeric columns
df_agg = df_all.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Convert aggregated columns to int
df_agg = df_agg.astype({
    "ELIGIBLE_VOTERS": int,
    "POLLS": int,
    "EARLY_VOING": int,
    "ABSENTEE": int,
    "PROVISIONAL": int
})

# Write output
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)