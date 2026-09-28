import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

# Convert IDs to integers by stripping prefixes
s0['Ship_id'] = s0['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
s1['Ord_id'] = s1['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s2['Prod_id'] = s2['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s3['Cust_id'] = s3['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
s4['Ship_id'] = s4['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
s4['Prod_id'] = s4['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
s4['Cust_id'] = s4['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Join Source5_50_4 with Source5_50_0 on Ship_id to get Ship_Date
joined_1 = pd.merge(s4, s0[['Ship_id', 'Ship_Date']], on='Ship_id', how='inner')

# Join with Source5_50_1 on Ord_id (to ensure valid orders)
joined_2 = pd.merge(joined_1, s1[['Ord_id']], on='Ord_id', how='inner')

# Join with Source5_50_2 on Prod_id (to ensure valid products)
joined_3 = pd.merge(joined_2, s2[['Prod_id']], on='Prod_id', how='inner')

# Join with Source5_50_3 on Cust_id (to ensure valid customers)
final_join = pd.merge(joined_3, s3[['Cust_id']], on='Cust_id', how='inner')

# Select only target columns
final = final_join[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id']]

# Ensure types match target schema
final['Ship_Date'] = final['Ship_Date'].astype(str)
final['Ord_id'] = final['Ord_id'].astype(int)
final['Prod_id'] = final['Prod_id'].astype(int)
final['Ship_id'] = final['Ship_id'].astype(int)

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)