import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_1.csv", index_col=0)

# Join on Store to bring StoreType to df0 rows
joined = pd.merge(df0, df1[['Store', 'StoreType']], on='Store', how='inner')

# Group by StoreType and count distinct Store
result = joined.groupby('StoreType', as_index=False).agg(Store=('Store', 'nunique'))

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_42/target_multisource_mcts.csv", index=False)