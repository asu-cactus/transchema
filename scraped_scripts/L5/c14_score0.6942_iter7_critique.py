import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv', index_col=0)
df4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv', index_col=0)

# Join all tables on their keys using inner joins
df = df2.merge(df0[['Cust_id']], on='Cust_id', how='inner')
df = df.merge(df1[['Ship_id']], on='Ship_id', how='inner')
df = df.merge(df3[['Prod_id']], on='Prod_id', how='inner')
df = df.merge(df4[['Ord_id']], on='Ord_id', how='inner')

# Convert string IDs to integers by removing prefixes
df['Ord_id'] = df['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
df['Prod_id'] = df['Prod_id'].str.replace('Prod_', '', regex=False).astype(int)
df['Cust_id'] = df['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)
df['Ship_id'] = df['Ship_id'].astype(str)

# Group by all keys to remove duplicates
result = df.groupby(['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id'], as_index=False).size()

# The groupby size() returns a 'size' column, drop it to keep only keys
result = result.drop(columns=['size'])

# Reorder columns to match target schema exactly
result = result[['Ship_id', 'Ord_id', 'Prod_id', 'Cust_id']]

result.to_csv('autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv', index=False)