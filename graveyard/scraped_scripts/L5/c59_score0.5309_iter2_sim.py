import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['Purchase Count'] = 1
df['Item Price'] = df['Price'].astype(int)
df['Total Purchase Value'] = df['Price'].astype(float)

result = df[['Purchase Count', 'Item Price', 'Total Purchase Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)