import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df = df0[['customer_id', 'date']].copy()
df['customer_id'] = df['customer_id'].astype(int)
df['date'] = df['date'].astype(str)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)