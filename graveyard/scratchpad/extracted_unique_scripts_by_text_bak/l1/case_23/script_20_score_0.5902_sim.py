import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)
df0 = df0[['customer_id', 'amount']]
df0['customer_id'] = df0['customer_id'].astype(int)
df0['amount'] = df0['amount'].astype(float)
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)