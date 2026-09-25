import pandas as pd
import re

# Read source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

# Join all tables on their keys
df = pd.merge(s4, s0, on='Ship_id', how='inner')
df = pd.merge(df, s1, on='Ord_id', how='inner')
df = pd.merge(df, s2[['Cust_id']], on='Cust_id', how='inner')
df = pd.merge(df, s3[['Prod_id']], on='Prod_id', how='inner')

# Group by Order_Priority and Ship_Mode
agg_df = df.groupby(['Order_Priority', 'Ship_Mode'], as_index=False).agg({
    'Ord_id': 'count',
    'Prod_id': 'count',
    'Ship_id': 'count',
    'Cust_id': 'count',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Rename count columns to match target schema integer IDs
agg_df = agg_df.rename(columns={
    'Ord_id': 'Ord_id',
    'Prod_id': 'Prod_id',
    'Ship_id': 'Ship_id',
    'Cust_id': 'Cust_id',
    'Sales': 'Sales',
    'Discount': 'Discount'
})

# Convert IDs from counts to integers (already int), Sales and Discount to int
agg_df['Ord_id'] = agg_df['Ord_id'].astype('Int64')
agg_df['Prod_id'] = agg_df['Prod_id'].astype('Int64')
agg_df['Ship_id'] = agg_df['Ship_id'].astype('Int64')
agg_df['Cust_id'] = agg_df['Cust_id'].astype('Int64')
agg_df['Sales'] = agg_df['Sales'].round().astype('Int64')
agg_df['Discount'] = (agg_df['Discount'] * 100).round().astype('Int64')

# Reorder columns to match target schema exactly
result = agg_df[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)