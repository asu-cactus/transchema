import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

# Join Source1 and Source2 on Ord_id
join_1_2 = pd.merge(s1, s2, on='Ord_id', how='inner')

# Join with Source4 on Prod_id
join_1_2_4 = pd.merge(join_1_2, s4, on='Prod_id', how='inner')

# Join with Source0 on Ship_id
join_all = pd.merge(join_1_2_4, s0, on='Ship_id', how='inner')

# Join with Source3 on Cust_id
join_all = pd.merge(join_all, s3, on='Cust_id', how='inner')

# Convert ID columns from strings like 'Ord_1082' to integers 1082
join_all['Ord_id'] = join_all['Ord_id'].str.extract(r'(\d+)').astype(int)
join_all['Prod_id'] = join_all['Prod_id'].str.extract(r'(\d+)').astype(int)
join_all['Ship_id'] = join_all['Ship_id'].str.extract(r'(\d+)').astype(int)
join_all['Cust_id'] = join_all['Cust_id'].str.extract(r'(\d+)').astype(int)

# Convert Sales to numeric (float), then sum aggregation will be correct
join_all['Sales'] = pd.to_numeric(join_all['Sales'], errors='coerce').fillna(0)

# Group by Product_Sub_Category, Order_Date, Ord_id
grouped = join_all.groupby(['Product_Sub_Category', 'Order_Date', 'Ord_id'], as_index=False).agg({
    'Sales': 'sum',
    'Prod_id': 'min',
    'Ship_id': 'min',
    'Cust_id': 'min'
})

# Reorder columns to match target schema
result = grouped[['Product_Sub_Category', 'Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

# Convert Sales to integer as in target schema
result['Sales'] = result['Sales'].round().astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)