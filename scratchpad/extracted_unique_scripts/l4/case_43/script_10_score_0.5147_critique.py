import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_43/training_3.csv", index_col=0)

# Concatenate all source tables (union)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Write output with exact target schema column order and names
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_mcts.csv", index=False)