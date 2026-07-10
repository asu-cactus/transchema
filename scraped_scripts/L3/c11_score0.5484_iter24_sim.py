import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)
df = df[['SN', 'Price']]
df['count'] = 1
df['SN'] = df['SN'].astype(str)
df['Price'] = df['Price'].astype(float)
df['count'] = df['count'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)