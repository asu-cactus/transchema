import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)

union_1_4 = pd.concat([s1, s4], ignore_index=True, sort=False)

join_1 = pd.merge(union_1_4, s0, how='inner', left_on='Ship_id', right_on='Ship_id')

join_2 = pd.merge(join_1, s2, how='inner', left_on='Cust_id', right_on='Cust_id')

join_3 = pd.merge(join_2, s3, how='inner', left_on='Prod_id', right_on='Prod_id')

df = join_3[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

df['Ord_id'] = df['Ord_id'].str.replace('Ord_', '').astype(int)
df['Ship_id'] = df['Ship_id'].str.replace('SHP_', '').astype(int)
df['Cust_id'] = df['Cust_id'].str.replace('Cust_', '').astype(int)
df['Sales'] = df['Sales'].round().astype(int)
df['Discount'] = (df['Discount'] * 100).round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)