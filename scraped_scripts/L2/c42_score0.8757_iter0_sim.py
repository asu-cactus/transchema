import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_42/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['Store', 'StoreType']], on='Store', how='inner')

grouped = merged.groupby('StoreType', as_index=False)['Store'].sum()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_42/target_multisource_mcts.csv", index=False)