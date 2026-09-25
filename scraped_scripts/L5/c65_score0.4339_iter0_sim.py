import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

df = pd.merge(s0, s4, on='Ord_id', how='inner')
df = pd.merge(df, s2, on='Cust_id', how='inner')

df['Ord_id'] = df['Ord_id'].str.extract('(\d+)').astype(int)
df['Ship_id'] = df['Ship_id'].str.extract('(\d+)').astype(int)
df['Cust_id'] = df['Cust_id'].str.extract('(\d+)').astype(int)
df['Prod_id'] = df['Prod_id'].astype(str)
df['Order_Priority'] = df['Order_Priority'].astype(str)
df['Sales'] = df['Sales'].round().astype(int)
df['Discount'] = (df['Discount'] * 100).round().astype(int)

result = df[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)