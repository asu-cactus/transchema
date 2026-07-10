import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_1.csv", index_col=0)

joined = pd.merge(df1, df0[['city']], how='inner', on='city')

result = joined.groupby('city', as_index=False).agg({'driver_count': 'max'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_62/target_multisource_mcts.csv", index=False)