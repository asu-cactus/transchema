import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_64/training_0.csv", index_col=0)
df0['date'] = pd.to_datetime(df0['date'])
df0['month'] = df0['date'].dt.month

pivot_result = df0.pivot_table(index='customer_id', columns='month', values='amount', aggfunc='sum', fill_value=0)

pivot_result.columns = [f'amount_{col}' for col in pivot_result.columns]

pivot_result['amount_x'] = pivot_result.iloc[:, 0] if 1 in df0['month'].unique() else 0
pivot_result['amount_y'] = pivot_result.iloc[:, 1] if 2 in df0['month'].unique() else 0

if 'amount_1' in pivot_result.columns and 'amount_2' in pivot_result.columns:
    pivot_result['amount_x'] = pivot_result['amount_1']
    pivot_result['amount_y'] = pivot_result['amount_2']
elif 'amount_1' in pivot_result.columns:
    pivot_result['amount_x'] = pivot_result['amount_1']
    pivot_result['amount_y'] = 0
elif 'amount_2' in pivot_result.columns:
    pivot_result['amount_x'] = 0
    pivot_result['amount_y'] = pivot_result['amount_2']
else:
    pivot_result['amount_x'] = 0
    pivot_result['amount_y'] = 0

pivot_result['avg_amount_spent'] = pivot_result[['amount_x', 'amount_y']].replace(0, pd.NA).mean(axis=1).fillna(0)

result = pivot_result[['amount_x', 'amount_y', 'avg_amount_spent']].copy()
result.reset_index(inplace=True)

result['amount_x'] = result['amount_x'].astype(int)
result['amount_y'] = result['amount_y'].astype(float)
result['avg_amount_spent'] = result['avg_amount_spent'].astype(float)
result['customer_id'] = result['customer_id'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_64/target_multisource_mcts.csv", index=False)