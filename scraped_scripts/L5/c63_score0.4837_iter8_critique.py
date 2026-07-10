import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)  # Ord_id dimension
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)  # Cust_id dimension
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)  # Prod_id dimension
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)  # Ship_id dimension
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)  # Fact table

# Join all source tables on their keys
df = pd.merge(s4, s0[['Ord_id']], on='Ord_id', how='inner')
df = pd.merge(df, s1[['Cust_id']], on='Cust_id', how='inner')
df = pd.merge(df, s2[['Prod_id']], on='Prod_id', how='inner')
df = pd.merge(df, s3[['Ship_id']], on='Ship_id', how='inner')

# Group by the leftmost keys in target schema and aggregate Sales and Discount by sum
agg = df.groupby(['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id'], as_index=False).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

# Convert Ord_id, Ship_id, Cust_id from string IDs to integers by extracting numeric suffix
agg['Ord_id'] = agg['Ord_id'].str.extract(r'Ord_(\d+)').astype('Int64')
agg['Ship_id'] = agg['Ship_id'].str.extract(r'SHP_(\d+)').astype('Int64')
agg['Cust_id'] = agg['Cust_id'].str.extract(r'Cust_(\d+)').astype('Int64')

# Round Sales and Discount and convert to integer type
agg['Sales'] = agg['Sales'].round().astype('Int64')
agg['Discount'] = agg['Discount'].round().astype('Int64')

# Reorder columns to match target schema exactly
result = agg[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)