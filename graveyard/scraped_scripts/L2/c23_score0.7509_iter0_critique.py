import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

merged = pd.merge(df0[['city']], df1[['city', 'driver_count']], on='city', how='inner')

result = merged.drop_duplicates(subset=['city']).rename(columns={'driver_count': 'type'})

result['type'] = result['type'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)