import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_45/training_0.csv", index_col=0)

df = df0[['Item ID', 'Item Name', 'Price']].copy()
df['Item ID'] = df['Item ID'].astype(int)
df['Item Name'] = df['Item Name'].astype(str)
df['Price'] = df['Price'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_45/target_multisource_mcts.csv", index=False)