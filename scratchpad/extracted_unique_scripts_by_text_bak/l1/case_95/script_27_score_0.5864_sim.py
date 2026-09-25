import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
result = df0.groupby(['customer_id', 'date'], as_index=False).size()
result = result.rename(columns={'size': 'count'})  # count column created by size(), but target schema does not require it, so drop it
result = result[['customer_id', 'date']]
result['customer_id'] = result['customer_id'].astype(int)
result['date'] = result['date'].astype(str)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)