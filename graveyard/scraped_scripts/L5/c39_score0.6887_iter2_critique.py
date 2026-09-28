import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

# Join Source0 and Source1 on Ord_id
merged = pd.merge(source0, source1, on='Ord_id', how='inner')

# Join with Source2 on Ship_id
merged = pd.merge(merged, source2, on='Ship_id', how='inner')

# Join with Source3 on Cust_id
merged = pd.merge(merged, source3, on='Cust_id', how='inner')

# Join with Source4 on Prod_id
merged = pd.merge(merged, source4, on='Prod_id', how='inner')

# Select and rename columns as per target schema
result = merged[['Product_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].copy()

# Convert Prod_id, Ship_id, Cust_id to integers by stripping prefixes
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Ord_id and Product_Category remain strings
result['Ord_id'] = result['Ord_id'].astype(str)
result['Product_Category'] = result['Product_Category'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)