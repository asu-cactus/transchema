import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

# Join df4 with df0 on Prod_id
df = pd.merge(df4, df0, on='Prod_id', how='inner')

# Join with df1 on Cust_id
df = pd.merge(df, df1, on='Cust_id', how='inner')

# Join with df2 on Ord_id
df = pd.merge(df, df2, on='Ord_id', how='inner')

# Join with df3 on Order_ID (df2 and df3)
df = pd.merge(df, df3, on='Order_ID', how='inner')

# Group by Product_Category and sum Profit
result = df.groupby('Product_Category', as_index=False)['Profit'].sum()

# Project only Profit column to match target schema
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)