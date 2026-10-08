import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

# Convert keys in s0, s3, s4 to integer for join
s0['Cust_id'] = s0['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
s3['Prod_id'] = s3['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)

# Convert keys in s2 to integer for join
s2['Cust_id'] = s2['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
s2['Prod_id'] = s2['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s2['Ord_id'] = s2['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s2['Ship_id'] = s2['Ship_id'].astype(str)

# Convert keys in s1 Ship_id to string (already string but ensure)
s1['Ship_id'] = s1['Ship_id'].astype(str)

# Join s2 with s0 on Cust_id (inner join)
df = s2.merge(s0[['Cust_id']], on='Cust_id', how='inner')

# Join with s3 on Prod_id (inner join)
df = df.merge(s3[['Prod_id']], on='Prod_id', how='inner')

# Join with s4 on Ord_id (inner join)
df = df.merge(s4[['Ord_id']], on='Ord_id', how='inner')

# Join with s1 on Ship_id (inner join)
df = df.merge(s1[['Ship_id']], on='Ship_id', how='inner')

# Final projection to target schema
result = df[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)