import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)
df = df0[['customer_id', 'amount']].copy()
df['customer_id'] = df['customer_id'].astype(int)
df['amount'] = df['amount'].astype(float)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)