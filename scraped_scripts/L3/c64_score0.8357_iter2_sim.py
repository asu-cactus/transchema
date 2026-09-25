import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_64/training_0.csv", index_col=0)

pivoted = df0.pivot_table(index='customer_id', columns='amount', aggfunc='size', fill_value=0)

pivoted.columns = [f"amount_{int(col)}" for col in pivoted.columns]

pivoted = pivoted.reset_index()

if 'amount_1' not in pivoted.columns:
    pivoted['amount_1'] = 0
if 'amount_2' not in pivoted.columns:
    pivoted['amount_2'] = 0

pivoted['amount_x'] = pivoted['amount_1']
pivoted['amount_y'] = pivoted['amount_2'].astype(float)

avg_amount = df0.groupby('customer_id')['amount'].mean().reset_index(name='avg_amount_spent')

result = pivoted[['customer_id', 'amount_x', 'amount_y']].merge(avg_amount, on='customer_id', how='left')

result['amount_x'] = result['amount_x'].astype(int)
result['amount_y'] = result['amount_y'].astype(float)
result['avg_amount_spent'] = result['avg_amount_spent'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_64/target_multisource_mcts.csv", index=False)