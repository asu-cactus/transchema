import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

# Join source2 with source0 on Cust_id
df = pd.merge(source2, source0[['Cust_id']], on='Cust_id', how='inner')

# Join with source1 on Ship_id
df = pd.merge(df, source1[['Ship_id']], on='Ship_id', how='inner')

# Join with source3 on Prod_id
df = pd.merge(df, source3[['Prod_id']], on='Prod_id', how='inner')

# Join with source4 on Ord_id
df = pd.merge(df, source4[['Ord_id']], on='Ord_id', how='inner')

# Convert columns to target types and format
df['Ship_id'] = df['Ship_id'].astype(str)
df['Ord_id'] = df['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
df['Prod_id'] = df['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
df['Cust_id'] = df['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

result = df[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)