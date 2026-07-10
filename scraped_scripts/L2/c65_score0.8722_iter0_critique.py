import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_1.csv", index_col=0)

# Join on 'fname'
df_joined = pd.merge(df0, df1, how='inner', left_on='fname', right_on='fname')

# Count rows per 'fname'
result = df_joined.groupby('fname', as_index=False).size().rename(columns={'size': 'row_count'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_65/target_multisource_mcts.csv", index=False)