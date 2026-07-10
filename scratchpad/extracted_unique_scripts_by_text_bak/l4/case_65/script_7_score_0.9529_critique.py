import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

# Concatenate all source tables
df_union = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Ensure all columns are string type as per target schema
for col in ['Year', 'Category', 'Nominee', 'Movie', 'Winner']:
    df_union[col] = df_union[col].astype(str)

# Remove duplicate rows to match target row count and uniqueness
df_union = df_union.drop_duplicates()

# Save the result
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)