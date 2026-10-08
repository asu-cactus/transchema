import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

# Join source4 with source1 on Cust_id to get Customer_Segment
merged = pd.merge(source4, source1[['Cust_id', 'Customer_Segment']], on='Cust_id', how='inner')

# Join with source0 on Ord_id
merged = pd.merge(merged, source0[['Ord_id']], on='Ord_id', how='inner')

# Join with source2 on Prod_id
merged = pd.merge(merged, source2[['Prod_id']], on='Prod_id', how='inner')

# Join with source3 on Ship_id
merged = pd.merge(merged, source3[['Ship_id']], on='Ship_id', how='inner')

# Convert ID columns from strings like "Ord_1" to integers 1
def extract_int_id(s):
    # Extract trailing digits from string IDs
    return s.str.extract('(\d+)$').astype(int)

merged['Ord_id'] = extract_int_id(merged['Ord_id'])
merged['Prod_id'] = extract_int_id(merged['Prod_id'])
merged['Ship_id'] = extract_int_id(merged['Ship_id'])
merged['Cust_id'] = extract_int_id(merged['Cust_id'])

# Group by all target columns (no aggregation needed, just drop duplicates)
result = merged[['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].drop_duplicates()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)