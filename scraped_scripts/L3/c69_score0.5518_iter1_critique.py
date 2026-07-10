import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

df = pd.merge(df0[['city', 'type']], df1[['city', 'fare']], on='city', how='inner')
df = df[['city', 'type', 'fare']]
df['fare'] = df['fare'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)