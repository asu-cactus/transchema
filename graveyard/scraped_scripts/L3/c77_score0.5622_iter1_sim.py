import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_77/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['city', 'type']], on='city', how='inner')

result = merged[['city', 'type', 'fare']].copy()
result['fare'] = result['fare'].astype(float)
result['city'] = result['city'].astype(str)
result['type'] = result['type'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_77/target_multisource_mcts.csv", index=False)