import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

# Union all source tables since they share the same schema
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Ensure columns are in target order and type cast to string
df_all = df_all[['Year', 'Category', 'Nominee', 'Movie', 'Winner']].astype(str)

# Remove duplicates to match target row count and uniqueness
df_all = df_all.drop_duplicates()

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)