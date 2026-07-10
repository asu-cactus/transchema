import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

# Concatenate all source tables (UNION)
df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Ensure correct types
df = df.astype({
    'Year': str,
    'Category': str,
    'Nominee': str,
    'Movie': str,
    'Winner': str
})

# Group by the key columns to remove duplicates, aggregate Movie and Winner by first occurrence
df = df.groupby(['Year', 'Category', 'Nominee'], as_index=False).agg({
    'Movie': 'first',
    'Winner': 'first'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)