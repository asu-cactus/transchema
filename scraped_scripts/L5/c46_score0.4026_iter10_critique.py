import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)  # Customer
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)  # Shipping
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)  # Order
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)  # Product
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)  # Order details

# Join Source5_46_4 with Source5_46_2 on Ord_id
df = s4.merge(s2, on='Ord_id', how='inner')

# Join with Source5_46_0 on Cust_id to get Customer_Name
df = df.merge(s0[['Cust_id', 'Customer_Name']], on='Cust_id', how='inner')

# Join with Source5_46_3 on Prod_id
df = df.merge(s3[['Prod_id']], on='Prod_id', how='inner')

# Join with Source5_46_1 on Ship_id
df = df.merge(s1[['Ship_id']], on='Ship_id', how='inner')

# Convert Ord_id, Prod_id, Ship_id from string IDs to integers by extracting numeric suffixes
df['Ord_id'] = df['Ord_id'].str.extract(r'(\d+)').astype(int)
df['Prod_id'] = df['Prod_id'].str.extract(r'(\d+)').astype(int)
df['Ship_id'] = df['Ship_id'].str.extract(r'(\d+)').astype(int)

# Select columns as per target schema
result = df[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)