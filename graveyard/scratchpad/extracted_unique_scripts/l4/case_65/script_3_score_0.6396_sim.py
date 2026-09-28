import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv", index_col=0)

join_01 = pd.merge(df0, df1, on=['Year', 'Category', 'Nominee', 'Movie', 'Winner'], how='inner')
join_34 = pd.merge(df3, df4, on=['Year', 'Category', 'Nominee', 'Movie', 'Winner'], how='inner')

union_all = pd.concat([df2, join_01, join_34], ignore_index=True)

union_all = union_all.astype({
    'Year': str,
    'Category': str,
    'Nominee': str,
    'Movie': str,
    'Winner': str
})

union_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)