import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df = pd.concat([df0], ignore_index=True)
df = df[['customer_id', 'date']]
df['customer_id'] = df['customer_id'].astype(int)
df['date'] = df['date'].astype(str)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)