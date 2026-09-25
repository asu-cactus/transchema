import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

# Convert Prod_id, Ship_id, Cust_id in s0 to int for joining and final output
s0['Prod_id'] = s0['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s0['Ship_id'] = s0['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
s0['Cust_id'] = s0['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Convert Prod_id in s4 to int for join
s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)

# Join s0 and s4 on Prod_id
merged = pd.merge(s0, s4[['Product_Category', 'Prod_id']], on='Prod_id', how='inner')

# Join with s1 on Ord_id (string, no conversion needed)
merged = pd.merge(merged, s1[['Ord_id']], on='Ord_id', how='inner')

# Convert Ship_id in s2 to int for join
s2['Ship_id'] = s2['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)

# Join with s2 on Ship_id
merged = pd.merge(merged, s2[['Ship_id']], on='Ship_id', how='inner')

# Convert Cust_id in s3 to int for join
s3['Cust_id'] = s3['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Join with s3 on Cust_id
merged = pd.merge(merged, s3[['Cust_id']], on='Cust_id', how='inner')

# Select final columns as per target schema
result = merged[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

# Ensure types match target schema
result['Ord_id'] = result['Ord_id'].astype(str)
result['Prod_id'] = result['Prod_id'].astype(int)
result['Ship_id'] = result['Ship_id'].astype(int)
result['Cust_id'] = result['Cust_id'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)