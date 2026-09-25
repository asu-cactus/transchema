import pandas as pd

# Read all source CSV files with index_col=0 as per hint 22
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_10/training_4.csv",
]

dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables (concatenate)
df_union = pd.concat(dfs, ignore_index=True)

# Group by PRECINCT and sum all other columns
# Ensure columns are exactly as target schema
grouped = df_union.groupby("PRECINCT", as_index=False).agg({
    "ELIGIBLE_VOTERS": "sum",
    "POLLS": "sum",
    "EARLY_VOING": "sum",
    "ABSENTEE": "sum",
    "PROVISIONAL": "sum"
})

# Convert columns to integer type as in target schema
for col in ["ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"]:
    grouped[col] = grouped[col].astype(int)

# Write output CSV without index
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)