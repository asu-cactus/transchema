import pandas as pd

# Read source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

# Join all sources on their keys
df = pd.merge(s0, s1, how='inner', on='Ship_id')
df = pd.merge(df, s2, how='inner', on='Cust_id')
df = pd.merge(df, s3, how='inner', on='Prod_id')
df = pd.merge(df, s4, how='inner', on='Ord_id')

# Select relevant columns including Order_Priority from s4
df = df[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Convert IDs to integers after removing prefixes
df['Ord_id'] = df['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
df['Ship_id'] = df['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
df['Cust_id'] = df['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Aggregate Sales and Discount by sum grouped by Prod_id, Order_Priority, Ord_id
agg_df = df.groupby(['Prod_id', 'Order_Priority', 'Ord_id'], as_index=False).agg({
    'Ship_id': 'first',  # Ship_id, Cust_id are keys but not in group by, so take first
    'Cust_id': 'first',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Round Sales and convert to int
agg_df['Sales'] = agg_df['Sales'].round().astype(int)

# Discount is fraction, multiply by 100 and round to int
agg_df['Discount'] = (agg_df['Discount'] * 100).round().astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)