import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

# Join fact table with customer dimension
join_0 = s4.merge(s0[['Customer_Name', 'Cust_id']], on='Cust_id', how='inner')

# Join with shipping dimension
join_1 = join_0.merge(s1[['Ship_id']], on='Ship_id', how='inner')

# Join with order dimension
join_2 = join_1.merge(s2[['Ord_id']], on='Ord_id', how='inner')

# Join with product dimension
join_3 = join_2.merge(s3[['Prod_id']], on='Prod_id', how='inner')

# Select target columns
result = join_3[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

# Convert IDs to integers by stripping prefixes
result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)

# Group by Customer_Name and Ord_id to remove duplicates, take first Prod_id and Ship_id
result = result.groupby(['Customer_Name', 'Ord_id'], as_index=False).agg({
    'Prod_id': 'first',
    'Ship_id': 'first'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)