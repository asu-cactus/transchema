import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

# Join s2 and s4 on Ord_id
df = pd.merge(s2, s4, on='Ord_id', how='inner')

# Join with s0 on Order_ID and Ship_id
df = pd.merge(df, s0, on=['Order_ID', 'Ship_id'], how='inner')

# Join with s1 on Prod_id
df = pd.merge(df, s1, on='Prod_id', how='inner')

# Join with s3 on Cust_id
df = pd.merge(df, s3, on='Cust_id', how='inner')

# Group by Order_ID and sum Profit
result = df.groupby('Order_ID', as_index=False)['Profit'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)