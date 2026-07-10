import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_23/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)
df = df[['customer_id', 'amount']]
df['customer_id'] = df['customer_id'].astype(int)
df['amount'] = df['amount'].astype(float)

df.to_csv('autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv', index=False)