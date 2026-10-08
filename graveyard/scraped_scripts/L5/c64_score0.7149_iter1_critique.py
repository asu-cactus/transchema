import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_4.csv", index_col=0)

# Join Source5_64_2 with Source5_64_0 on Cust_id
df = s2.merge(s0[['Customer_Name', 'Cust_id']], on='Cust_id', how='inner')

# Join with Source5_64_1 on Ship_id
df = df.merge(s1[['Ship_Date', 'Ship_id']], on='Ship_id', how='inner')

# Join with Source5_64_3 on Ord_id
df = df.merge(s3[['Order_Date', 'Ord_id']], on='Ord_id', how='inner')

# Join with Source5_64_4 on Prod_id (to use all source tables)
df = df.merge(s4[['Prod_id']], on='Prod_id', how='inner')

# Fill Ship_Date with Order_Date where Ship_Date is null
df['Ship_Date'] = df['Ship_Date'].fillna(df['Order_Date'])
df = df.drop(columns=['Order_Date'])

# Convert IDs to integers by removing prefixes
df['Ord_id'] = df['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
df['Prod_id'] = df['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
df['Ship_id'] = df['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)

# Group by all target columns to remove duplicates
grouped = df.groupby(['Ship_Date', 'Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id'], as_index=False).agg({'Ord_id':'count'})

# Project final columns as per target schema (drop the aggregation count column)
result = grouped[['Ship_Date', 'Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)