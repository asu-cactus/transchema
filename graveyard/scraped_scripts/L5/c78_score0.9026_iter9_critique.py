import pandas as pd

# Read source files with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_4.csv", index_col=0)

# Join s3 (fact table) with s0 on Cust_id
df = pd.merge(s3, s0, on='Cust_id', how='inner')

# Join with s1 on Ship_id
df = pd.merge(df, s1, on='Ship_id', how='inner')

# Join with s2 on Ord_id
df = pd.merge(df, s2, on='Ord_id', how='inner')

# Join with s4 on Prod_id
df = pd.merge(df, s4, on='Prod_id', how='inner')

# Group by Customer_Segment and aggregate sum of Profit
agg_df = df.groupby('Customer_Segment', as_index=False)['Profit'].sum()

# Output only the Profit column as per target schema
result = agg_df[['Profit']]

# Write to CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv", index=False)