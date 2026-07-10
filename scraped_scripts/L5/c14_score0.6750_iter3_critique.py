import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

# Join Source2 and Source3 on Prod_id
df = pd.merge(source2, source3, left_on='Prod_id', right_on='Prod_id', how='inner')

# Join with Source0 on Cust_id
df = pd.merge(df, source0, left_on='Cust_id', right_on='Cust_id', how='inner')

# Join with Source4 on Ord_id
df = pd.merge(df, source4, left_on='Ord_id', right_on='Ord_id', how='inner')

# Join with Source1 on Ship_id
df = pd.merge(df, source1, left_on='Ship_id', right_on='Ship_id', how='inner')

# Select and convert columns to target schema
result = df[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']].copy()

# Convert Ship_id to string (already string but ensure)
result['Ship_id'] = result['Ship_id'].astype(str)

# Convert Ord_id, Prod_id, Cust_id from strings like 'Ord_1082' to integers
result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Remove duplicates if any (not strictly required but safe)
result = result.drop_duplicates()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)