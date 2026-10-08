import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)
df = df1[['city', 'fare']].copy()
df['type'] = pd.NA
df = df[['city', 'type', 'fare']]
df['fare'] = df['fare'].astype(float)
df.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)