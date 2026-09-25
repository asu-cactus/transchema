import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)  # Customer
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)  # Order
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)  # Shipping
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)  # Product
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)  # Fact table

# Join df4 with df1 on Ord_id
df = pd.merge(df4, df1, on='Ord_id', how='inner')

# Join with df2 on Ship_id
df = pd.merge(df, df2, on='Ship_id', how='inner')

# Join with df0 on Cust_id
df = pd.merge(df, df0, on='Cust_id', how='inner')

# Join with df3 on Prod_id
df = pd.merge(df, df3, on='Prod_id', how='inner')

# Group by 'Region' and sum 'Profit'
agg_df = df.groupby('Region', as_index=False)['Profit'].sum()

# Output only the 'Profit' column as in target schema
result = agg_df[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)