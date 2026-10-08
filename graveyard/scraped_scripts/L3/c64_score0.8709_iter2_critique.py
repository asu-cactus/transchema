import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_64/training_0.csv", index_col=0)

agg = df0.groupby('customer_id')['amount'].agg(['sum', 'mean']).reset_index()

agg = agg.rename(columns={'sum': 'amount_x', 'mean': 'avg_amount_spent'})

agg['amount_y'] = 0.0

agg['customer_id'] = agg['customer_id'].astype(int)
agg['amount_x'] = agg['amount_x'].astype(int)
agg['amount_y'] = agg['amount_y'].astype(float)
agg['avg_amount_spent'] = agg['avg_amount_spent'].astype(float)

result = agg[['customer_id', 'amount_x', 'amount_y', 'avg_amount_spent']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_64/target_multisource_mcts.csv", index=False)