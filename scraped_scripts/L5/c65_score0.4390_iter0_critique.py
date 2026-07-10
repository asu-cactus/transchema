import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

# Join s0 with s4 on Ord_id
df = pd.merge(s0, s4, on='Ord_id', how='inner')

# Join with s1 on Ship_id
df = pd.merge(df, s1, on='Ship_id', how='inner')

# Join with s2 on Cust_id
df = pd.merge(df, s2, on='Cust_id', how='inner')

# Join with s3 on Prod_id
df = pd.merge(df, s3, on='Prod_id', how='inner')

# Convert IDs to integers by extracting digits
df['Ord_id'] = df['Ord_id'].str.extract('(\d+)').astype(int)
df['Ship_id'] = df['Ship_id'].str.extract('(\d+)').astype(int)
df['Cust_id'] = df['Cust_id'].str.extract('(\d+)').astype(int)

# Ensure Prod_id and Order_Priority are strings
df['Prod_id'] = df['Prod_id'].astype(str)
df['Order_Priority'] = df['Order_Priority'].astype(str)

# Round and convert Sales and Discount to integers
df['Sales'] = df['Sales'].round().astype(int)
df['Discount'] = (df['Discount'] * 100).round().astype(int)

# Group by the primary key columns and aggregate Sales and Discount by sum
result = df.groupby(
    ['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id'],
    as_index=False
).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

# Reorder columns to match target schema exactly
result = result[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)