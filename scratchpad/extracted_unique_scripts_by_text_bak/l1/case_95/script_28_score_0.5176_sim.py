import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
grouped = df0.groupby(['customer_id', 'date'], as_index=False).agg({'customer_id':'count'})
grouped = grouped.rename(columns={'customer_id': 'customer_id'})
grouped['date'] = grouped['date'].astype(str)
grouped = grouped[['customer_id', 'date']]
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)