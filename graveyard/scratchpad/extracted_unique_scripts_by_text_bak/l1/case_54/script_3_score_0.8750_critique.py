import pandas as pd

# List all source files (assuming 5 source files named training_0.csv to training_4.csv)
file_paths = [
    "autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_4.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_all.groupby("condition", as_index=False)["click"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)