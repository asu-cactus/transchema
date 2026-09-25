import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

# The JOIN operations in the plan are redundant here because all source tables have the same schema.
# The final step is to UNION all source tables.

df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Ensure columns are strings as per target schema
for col in ['Year', 'Category', 'Nominee', 'Movie', 'Winner']:
    df_all[col] = df_all[col].astype(str)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)