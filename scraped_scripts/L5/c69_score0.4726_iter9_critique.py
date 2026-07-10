import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

# Join source3 with source1 on Ord_id
df = pd.merge(source3, source1, on='Ord_id', how='inner')

# Join with source4 on Ship_id
df = pd.merge(df, source4, on='Ship_id', how='inner')

# Join with source2 on Cust_id
df = pd.merge(df, source2, on='Cust_id', how='inner')

# Join with source0 on Prod_id
df = pd.merge(df, source0, on='Prod_id', how='inner')

# Select target columns
result = df[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].copy()

# Convert IDs to integers by removing prefixes
result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Group by all columns to remove duplicates (no aggregation needed)
result = result.drop_duplicates(subset=['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)