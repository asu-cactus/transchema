import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)

df['Broadband Initiative'] = df['Broadband Initiative'].astype(int)
df['Federal'] = df['Federal'].astype(int)
df['Percent'] = df['Percent'].astype(float)
df['state'] = df['state'].astype(str)
df['population'] = df['population'].astype(int) if 'population' in df.columns else 0

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)