import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_4.csv", index_col=0)

# Join df4 with df1 on Ord_id (inner join to avoid unmatched rows)
df = df4.merge(df1, on='Ord_id', how='inner')

# Join with df0 on Prod_id
df = df.merge(df0, on='Prod_id', how='inner')

# Join with df3 on Ship_id
df = df.merge(df3, on='Ship_id', how='inner')

# Join with df2 on Cust_id
df = df.merge(df2, on='Cust_id', how='inner')

# Group by Product_Category and Product_Sub_Category, aggregate sum of Profit
result = df.groupby(['Product_Category', 'Product_Sub_Category'], as_index=False)['Profit'].sum()

# Select only Profit column to match target schema
result = result[['Profit']]

# Ensure Profit is float type
result['Profit'] = result['Profit'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_74/target_multisource_mcts.csv", index=False)