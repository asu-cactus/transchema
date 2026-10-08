import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

# Join Source5_83_4 with Source5_83_0 on Cust_id
df = pd.merge(df4, df0, on='Cust_id', how='inner')

# Join with Source5_83_1 on Ord_id
df = pd.merge(df, df1, on='Ord_id', how='inner')

# Join with Source5_83_2 on Ship_id
df = pd.merge(df, df2, on='Ship_id', how='inner')

# Join with Source5_83_3 on Prod_id
df = pd.merge(df, df3, on='Prod_id', how='inner')

# Group by Customer_Segment and aggregate average Profit
result = df.groupby('Customer_Segment', as_index=False)['Profit'].mean()

# Output only Profit column as per target schema
result = result[['Profit']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)