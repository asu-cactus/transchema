import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

# Join s4 with s0 on Ord_id
df = pd.merge(s4, s0[['Ord_id']], on='Ord_id', how='inner')

# Join with s1 on Cust_id
df = pd.merge(df, s1[['Cust_id']], on='Cust_id', how='inner')

# Join with s2 on Prod_id
df = pd.merge(df, s2[['Prod_id']], on='Prod_id', how='inner')

# Join with s3 on Ship_id
df = pd.merge(df, s3[['Ship_id']], on='Ship_id', how='inner')

# Group by Prod_id
agg_df = df.groupby('Prod_id', as_index=False).agg({
    'Ord_id': 'first',
    'Ship_id': 'first',
    'Cust_id': 'first',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Convert Ord_id, Ship_id, Cust_id from strings like "Ord_1082" to int 1082
agg_df['Ord_id'] = agg_df['Ord_id'].str.extract(r'(\d+)').astype(int)
agg_df['Ship_id'] = agg_df['Ship_id'].str.extract(r'(\d+)').astype(int)
agg_df['Cust_id'] = agg_df['Cust_id'].str.extract(r'(\d+)').astype(int)

# Round Sales to int
agg_df['Sales'] = agg_df['Sales'].round().astype(int)

# Convert Discount fraction to integer percentage
agg_df['Discount'] = (agg_df['Discount'] * 100).round().astype(int)

# Reorder columns as per target schema
result = agg_df[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)