import pandas as pd

# List all source files (assuming 10 source files named training_0.csv to training_9.csv)
file_paths = [
    f"autopipeline-benchmarks/github-pipelines/length1_22/training_{i}.csv" for i in range(10)
]

# Read all source tables into a list of dataframes
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

# Union all source tables by concatenation
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and sum 'click'
result = df_all.groupby("condition", as_index=False)["click"].sum()

# Write the result to the target file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)