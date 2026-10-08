import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on='city', how='inner')

result = merged.groupby('city', as_index=False).agg(type=('driver_count', 'first'))

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)