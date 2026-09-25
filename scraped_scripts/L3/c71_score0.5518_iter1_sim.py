import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_71/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_71/training_1.csv', index_col=0)

merged = pd.merge(df0[['city', 'type']], df1[['city', 'fare']], on='city')

result = merged[['city', 'type', 'fare']].copy()
result['city'] = result['city'].astype(str)
result['type'] = result['type'].astype(str)
result['fare'] = result['fare'].astype(float)

result.to_csv('autopipeline-benchmarks/github-pipelines/length3_71/target_multisource_mcts.csv', index=False)