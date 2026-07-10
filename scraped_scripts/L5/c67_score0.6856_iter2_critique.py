import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

# Convert IDs in s2
s2['Ship_id'] = s2['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
s2['Ord_id'] = s2['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s2['Cust_id'] = s2['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Convert IDs in s1
s1['Ship_id'] = s1['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)

# Convert IDs in s3
s3['Cust_id'] = s3['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Convert IDs in s4
s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)

# Join s2 with s0 on Prod_id
df = s2.merge(s0[['Prod_id']], on='Prod_id', how='inner')

# Join with s1 on Ship_id
df = df.merge(s1[['Ship_id', 'Ship_Date']], on='Ship_id', how='inner')

# Join with s3 on Cust_id
df = df.merge(s3[['Cust_id']], on='Cust_id', how='inner')

# Join with s4 on Ord_id
df = df.merge(s4[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

# Rename Order_Date to Ship_Date (target schema expects Ship_Date)
df = df.rename(columns={'Order_Date': 'Ship_Date'})

# Select only target columns in order
df = df[['Ship_Date', 'Prod_id', 'Ord_id', 'Ship_id', 'Cust_id']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)