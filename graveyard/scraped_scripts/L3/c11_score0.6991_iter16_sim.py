import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)

df = df0[['SN', 'Price']].copy()
df['count'] = 1
df['Price'] = df['Price'].astype(float)
df['SN'] = df['SN'].astype(str)
df['count'] = df['count'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)