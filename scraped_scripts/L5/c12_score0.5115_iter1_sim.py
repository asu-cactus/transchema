import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

pivot = s0.pivot(index='Ship_id', columns='Ship_Mode', values='Ship_id')
pivot = pivot.reset_index()
pivot = pivot.melt(id_vars='Ship_id', value_name='Ship_id_val').dropna(subset=['Ship_id_val'])
pivot = pivot.rename(columns={'variable': 'Ship_Mode'}).drop(columns=['Ship_id_val'])

df = pd.merge(pivot, s4, on='Ship_id', how='inner')
df = pd.merge(df, s1, on='Ord_id', how='inner')
df = pd.merge(df, s2[['Cust_id']], on='Cust_id', how='inner')
df = pd.merge(df, s3[['Prod_id']], on='Prod_id', how='inner')

df['Sales'] = df['Sales'].round().astype('Int64')
df['Discount'] = (df['Discount'] * 100).round().astype('Int64')

result = df[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)