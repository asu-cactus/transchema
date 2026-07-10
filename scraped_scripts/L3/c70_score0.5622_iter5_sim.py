import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_70/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_70/training_1.csv", index_col=0)

df = pd.merge(df0, df1[['city', 'type']], on='city')

result = df[['city', 'type', 'fare']].copy()
result['fare'] = result['fare'].astype(float)
result['city'] = result['city'].astype(str)
result['type'] = result['type'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_70/target_multisource_mcts.csv", index=False)