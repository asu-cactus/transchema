import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_20/training_0.csv", index_col=0)

df0['SN'] = df0['SN'].astype(str)
df0['Price'] = df0['Price'].astype(float)

df = df0.groupby('SN', as_index=False).agg({'Price': 'sum'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_20/target_multisource_mcts.csv", index=False)