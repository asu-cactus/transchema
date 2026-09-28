import pandas as pd

# Read all source tables (assuming 4 source tables as implied by the target tuple count and instructions)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_3.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by 'sex' and 'smoker' and compute mean of 'tip_pct'
result = df_all.groupby(['sex', 'smoker'], as_index=False)['tip_pct'].mean()

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)