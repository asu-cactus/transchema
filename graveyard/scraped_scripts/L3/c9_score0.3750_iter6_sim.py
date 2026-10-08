import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_9/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_9/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)
df = df[['park_name', 'observations']]
df['park_name'] = df['park_name'].astype(str)
df['observations'] = pd.to_numeric(df['observations'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_9/target_multisource_mcts.csv", index=False)