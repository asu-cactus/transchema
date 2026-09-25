import pandas as pd

# Read all source tables with index_col=0 to ignore the first column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

# Strip whitespace from string ID columns to ensure clean joins
s0['Ship_id'] = s0['Ship_id'].str.strip()
s2['Ship_id'] = s2['Ship_id'].str.strip()

# Join Source5_39_0 and Source5_39_2 on Ship_id
join_0_2 = pd.merge(s0, s2, on='Ship_id', how='inner')

# Strip Prod_id strings for clean join
s4['Prod_id'] = s4['Prod_id'].str.strip()
join_0_2['Prod_id'] = join_0_2['Prod_id'].str.strip()

# Join with Source5_39_4 on Prod_id to get Product_Category
join_0_2_4 = pd.merge(join_0_2, s4[['Prod_id', 'Product_Category']], on='Prod_id', how='inner')

# Strip Cust_id strings for clean join
s3['Cust_id'] = s3['Cust_id'].str.strip()
join_0_2_4['Cust_id'] = join_0_2_4['Cust_id'].str.strip()

# Join with Source5_39_3 on Cust_id
join_0_2_4_3 = pd.merge(join_0_2_4, s3[['Cust_id']], on='Cust_id', how='inner')

# Strip Ord_id strings for clean join
s1['Ord_id'] = s1['Ord_id'].str.strip()
join_0_2_4_3['Ord_id'] = join_0_2_4_3['Ord_id'].str.strip()

# Join with Source5_39_1 on Ord_id to use all source tables
final_join = pd.merge(join_0_2_4_3, s1[['Ord_id']], on='Ord_id', how='inner')

# Convert Prod_id, Ship_id, Cust_id to integers by removing prefixes
final_join['Prod_id'] = final_join['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
final_join['Ship_id'] = final_join['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
final_join['Cust_id'] = final_join['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Group by Ord_id to remove duplicates (no aggregation needed)
result = final_join[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].drop_duplicates().groupby('Ord_id', as_index=False).first()

# Reorder columns to match target schema exactly
result = result[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

# Write to output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)