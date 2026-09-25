import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_4.csv", index_col=0)

# Join s4 with s1 on Ord_id
df = pd.merge(s4, s1, how='inner', on='Ord_id')

# Join with s0 on Prod_id
df = pd.merge(df, s0, how='inner', on='Prod_id')

# Join with s3 on Ship_id
df = pd.merge(df, s3, how='inner', on='Ship_id')

# Join with s2 on Cust_id
df = pd.merge(df, s2, how='inner', on='Cust_id')

# Convert Profit to numeric
df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')

# Group by Order_Priority and sum Profit
result = df.groupby('Order_Priority', as_index=False)['Profit'].sum()

# Project only Profit column to match target schema
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_74/target_multisource_mcts.csv", index=False)