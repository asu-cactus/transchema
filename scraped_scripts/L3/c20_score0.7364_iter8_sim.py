import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_20/training_0.csv", index_col=0)

df = df0[['SN', 'Price']].copy()
df['Price'] = df['Price'].astype(float)
df['SN'] = df['SN'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_20/target_multisource_mcts.csv", index=False)