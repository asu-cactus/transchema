import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

# Join Source0 and Source1 on Ord_id
j01 = pd.merge(s0, s1, on='Ord_id', how='inner')

# Join with Source2 on Ship_id
j012 = pd.merge(j01, s2, on='Ship_id', how='inner')

# Join with Source3 on Cust_id
j0123 = pd.merge(j012, s3, on='Cust_id', how='inner')

# Join with Source4 on Prod_id
j01234 = pd.merge(j0123, s4, on='Prod_id', how='inner')

# Convert Prod_id, Ship_id, Cust_id to integers by stripping prefixes
j01234['Prod_id'] = j01234['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
j01234['Ship_id'] = j01234['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
j01234['Cust_id'] = j01234['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Group by Ord_id to remove duplicates if any (no aggregation needed)
result = j01234.drop_duplicates(subset=['Ord_id'])

# Select columns in target schema order
result = result[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)