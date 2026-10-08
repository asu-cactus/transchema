import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

# Join Source4 with Source0 on Ord_id
df = pd.merge(s4, s0[['Ord_id']], on='Ord_id', how='inner')

# Join with Source1 on Cust_id
df = pd.merge(df, s1[['Cust_id']], on='Cust_id', how='inner')

# Join with Source2 on Prod_id
df = pd.merge(df, s2[['Prod_id']], on='Prod_id', how='inner')

# Join with Source3 on Ship_id
df = pd.merge(df, s3[['Ship_id']], on='Ship_id', how='inner')

# Select target columns
df = df[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Convert columns to correct types
df['Ord_id'] = pd.to_numeric(df['Ord_id'], errors='coerce').fillna(0).astype(int)
df['Ship_id'] = pd.to_numeric(df['Ship_id'], errors='coerce').fillna(0).astype(int)
df['Cust_id'] = pd.to_numeric(df['Cust_id'], errors='coerce').fillna(0).astype(int)
df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0).astype(int)
df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0).astype(int)

# Group by Prod_id and aggregate
result = df.groupby('Prod_id').agg({
    'Ord_id': 'count',
    'Ship_id': 'count',
    'Cust_id': 'count',
    'Sales': 'sum',
    'Discount': 'sum'
}).reset_index()

# Rename columns to match target schema exactly
result.columns = ['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)