import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

# Join Source4 (fact) with Source0 (customer) on Cust_id
df = pd.merge(df4, df0[['Cust_id', 'Customer_Name']], on='Cust_id', how='inner')

# Join with Source2 (order) on Ord_id
df = pd.merge(df, df2[['Ord_id']], on='Ord_id', how='inner')

# Join with Source3 (product) on Prod_id
df = pd.merge(df, df3[['Prod_id']], on='Prod_id', how='inner')

# Join with Source1 (shipping) on Ship_id
df = pd.merge(df, df1[['Ship_id']], on='Ship_id', how='inner')

# Extract numeric parts from Ord_id, Prod_id, Ship_id to convert to integers
df['Ord_id'] = df['Ord_id'].str.extract(r'(\d+)').astype(int)
df['Prod_id'] = df['Prod_id'].str.extract(r'(\d+)').astype(int)
df['Ship_id'] = df['Ship_id'].str.extract(r'(\d+)').astype(int)

# Select and reorder columns as per target schema
result = df[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

# Group by all columns to remove duplicates (target has unique rows)
result = result.groupby(['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id'], as_index=False).first()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)