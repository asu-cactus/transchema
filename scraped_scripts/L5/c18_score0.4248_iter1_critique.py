import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Join s1 with s4 on Ship_id to get Ship_Mode
df = s1.merge(s4[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')

# Join with s0 on Prod_id (to use all source tables, even if not projected)
df = df.merge(s0[['Prod_id']], on='Prod_id', how='inner')

# Join with s2 on Ord_id
df = df.merge(s2[['Ord_id']], on='Ord_id', how='inner')

# Join with s3 on Cust_id
df = df.merge(s3[['Cust_id']], on='Cust_id', how='inner')

# Group by the leftmost key columns plus Ship_Mode, aggregate sums of Order_Quantity and Sales
result = df.groupby(['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Ship_Mode'], as_index=False).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum'
})

# Reorder columns to match target schema: ['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']
result = result[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

# Convert IDs and numeric columns to int as per target schema
result['Order_Quantity'] = result['Order_Quantity'].astype(int)
result['Sales'] = result['Sales'].astype(int)
result['Ord_id'] = result['Ord_id'].str.extract('(\d+)').astype(int)
result['Prod_id'] = result['Prod_id'].str.extract('(\d+)').astype(int)
result['Ship_id'] = result['Ship_id'].str.extract('(\d+)').astype(int)
result['Cust_id'] = result['Cust_id'].str.extract('(\d+)').astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)