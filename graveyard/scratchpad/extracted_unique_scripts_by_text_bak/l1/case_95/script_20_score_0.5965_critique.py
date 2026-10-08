import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df0 = df0[['customer_id', 'date']]
df0 = df0.astype({'customer_id': int, 'date': str})
df0 = df0.drop_duplicates(subset=['customer_id', 'date'])
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)