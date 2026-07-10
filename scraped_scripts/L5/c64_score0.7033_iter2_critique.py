import pandas as pd

# Read source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_4.csv", index_col=0)

# Join Source5_64_2 (fact) with Source5_64_0 (customer) on Cust_id
join_0 = pd.merge(s2, s0[['Customer_Name', 'Cust_id']], how='inner', on='Cust_id')

# Join with Source5_64_1 (shipping) on Ship_id
join_1 = pd.merge(join_0, s1[['Ship_Date', 'Ship_id']], how='inner', on='Ship_id')

# Join with Source5_64_3 (order) on Ord_id
join_2 = pd.merge(join_1, s3[['Order_Date', 'Ord_id']], how='inner', on='Ord_id')

# Join with Source5_64_4 (product) on Prod_id (to ensure Prod_id validity)
join_3 = pd.merge(join_2, s4[['Prod_id']], how='inner', on='Prod_id')

# Select and rename columns to match target schema
final = join_3[['Ship_Date', 'Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']].copy()

# Convert IDs from string to integer by removing prefixes
final['Ord_id'] = final['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
final['Prod_id'] = final['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
final['Ship_id'] = final['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)

# Ensure Ship_Date and Customer_Name are strings
final['Ship_Date'] = final['Ship_Date'].astype(str)
final['Customer_Name'] = final['Customer_Name'].astype(str)

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)