import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

# Join source4 with source0 on Cust_id
join_0 = pd.merge(source4, source0, how='inner', left_on='Cust_id', right_on='Cust_id')

# Join with source1 on Ship_id
join_1 = pd.merge(join_0, source1, how='inner', left_on='Ship_id', right_on='Ship_id')

# Join with source2 on Ord_id
join_2 = pd.merge(join_1, source2, how='inner', left_on='Ord_id', right_on='Ord_id')

# Join with source3 on Prod_id
join_3 = pd.merge(join_2, source3, how='inner', left_on='Prod_id', right_on='Prod_id')

# Extract integer IDs from string IDs for Ord_id, Prod_id, Ship_id
# Example: 'Ord_1082' -> 1082
join_3['Ord_id'] = join_3['Ord_id'].str.extract(r'(\d+)').astype(int)
join_3['Prod_id'] = join_3['Prod_id'].str.extract(r'(\d+)').astype(int)
join_3['Ship_id'] = join_3['Ship_id'].str.extract(r'(\d+)').astype(int)

# Select target columns
result = join_3[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

# Group by all target columns to ensure uniqueness (no aggregation needed)
result = result.drop_duplicates()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)