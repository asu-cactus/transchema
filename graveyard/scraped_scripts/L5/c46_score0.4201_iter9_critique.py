import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

# Join source4 (fact) with source0 (customer) on Cust_id
join_4_0 = pd.merge(source4, source0[['Customer_Name', 'Cust_id']], on='Cust_id', how='inner')

# Join with source1 (shipping) on Ship_id
join_4_0_1 = pd.merge(join_4_0, source1[['Ship_id']], on='Ship_id', how='inner')

# Join with source2 (order) on Ord_id
join_4_0_1_2 = pd.merge(join_4_0_1, source2[['Ord_id']], on='Ord_id', how='inner')

# Join with source3 (product) on Prod_id
join_all = pd.merge(join_4_0_1_2, source3[['Prod_id']], on='Prod_id', how='inner')

# Convert Ord_id, Prod_id, Ship_id from strings like "Ord_1082" to integers 1082
join_all['Ord_id'] = join_all['Ord_id'].str.extract(r'(\d+)').astype(int)
join_all['Prod_id'] = join_all['Prod_id'].str.extract(r'(\d+)').astype(int)
join_all['Ship_id'] = join_all['Ship_id'].str.extract(r'(\d+)').astype(int)

# Select and reorder columns as per target schema
target = join_all[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']].copy()

# Write output
target.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)