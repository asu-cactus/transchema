import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
agg = df0.groupby(['customer_id', 'date'], as_index=False)['amount'].sum()
agg['customer_id'] = agg['customer_id'].astype(int)
agg['date'] = agg['date'].astype(str)
agg = agg[['customer_id', 'date']]
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)