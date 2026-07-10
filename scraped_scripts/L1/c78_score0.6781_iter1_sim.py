import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)
df = pd.concat([df0], ignore_index=True)
df = df[['Product', 'Price']]
df['Product'] = df['Product'].astype(str)
df['Price'] = df['Price'].astype(float)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)