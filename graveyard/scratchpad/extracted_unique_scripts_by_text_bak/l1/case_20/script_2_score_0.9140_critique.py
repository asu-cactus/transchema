import pandas as pd

# List all source files (assuming 4 source files as per naming pattern)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_20/training_3.csv"
]

# Read all source tables into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# UNION all source tables (concatenate)
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY 'sex' and 'smoker' and aggregate mean on numeric columns
grouped = df_all.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Ensure correct types as per target schema
grouped['sex'] = grouped['sex'].astype(str)
grouped['smoker'] = grouped['smoker'].astype(str)
grouped['total_bill'] = grouped['total_bill'].astype(float)
grouped['tip'] = grouped['tip'].astype(float)
grouped['size'] = grouped['size'].astype(float)

# Write output to target file
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)