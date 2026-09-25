import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

# Join Source5_89_4 with Source5_89_2 on Ord_id
df = pd.merge(df4, df2, on='Ord_id', how='inner')

# Join with Source5_89_3 on Ship_id
df = pd.merge(df, df3, on='Ship_id', how='inner')

# Join with Source5_89_1 on Cust_id
df = pd.merge(df, df1, on='Cust_id', how='inner')

# Join with Source5_89_0 on Prod_id
df = pd.merge(df, df0, on='Prod_id', how='inner')

# Group by Ord_id and sum Profit
result = df.groupby('Ord_id', dropna=False)['Profit'].sum().reset_index()

# Keep only Profit column as per target schema
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)