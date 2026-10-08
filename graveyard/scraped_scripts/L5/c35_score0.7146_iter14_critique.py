import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

# Convert string IDs to integers in s0
s0['Ord_id'] = s0['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s0['Prod_id'] = s0['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s0['Cust_id'] = s0['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Convert Prod_id in s1
s1['Prod_id'] = s1['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)

# Convert Cust_id in s3
s3['Cust_id'] = s3['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Convert Ord_id in s4
s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)

# Join s0 and s1 on Prod_id
df = pd.merge(s0, s1[['Prod_id', 'Product_Category']], on='Prod_id', how='inner')

# Join with s2 on Ship_id
df = pd.merge(df, s2[['Ship_id']], on='Ship_id', how='inner')

# Join with s3 on Cust_id
df = pd.merge(df, s3[['Cust_id']], on='Cust_id', how='inner')

# Join with s4 on Ord_id
df = pd.merge(df, s4[['Ord_id']], on='Ord_id', how='inner')

# Group by the leftmost keys and sum Sales
result = df.groupby(['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id'], as_index=False)['Sales'].sum()

# Ensure column order and names match target schema
result = result[['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)