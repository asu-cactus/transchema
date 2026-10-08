import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)

joined = pd.merge(df1, df0[['city']], on='city', how='inner')

result = joined.groupby('city', as_index=False).agg({'driver_count': 'first'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_81/target_multisource_mcts.csv", index=False)