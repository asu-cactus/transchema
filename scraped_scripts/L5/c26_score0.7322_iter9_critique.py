import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

# Ensure key columns are string for joins
s1['Ord_id'] = s1['Ord_id'].astype(str)
s2['Ord_id'] = s2['Ord_id'].astype(str)
s1['Prod_id'] = s1['Prod_id'].astype(str)
s4['Prod_id'] = s4['Prod_id'].astype(str)
s1['Cust_id'] = s1['Cust_id'].astype(str)
s3['Cust_id'] = s3['Cust_id'].astype(str)
s1['Ship_id'] = s1['Ship_id'].astype(str)
s0['Ship_id'] = s0['Ship_id'].astype(str)

# Join tables stepwise
join_1 = pd.merge(s1, s2, on='Ord_id', how='inner')
join_2 = pd.merge(join_1, s0, on='Ship_id', how='inner')
join_3 = pd.merge(join_2, s3, on='Cust_id', how='inner')
join_4 = pd.merge(join_3, s4, on='Prod_id', how='inner')

# Group by Product_Sub_Category and Order_Date, aggregate Sales by sum,
# and take min of Ord_id, Prod_id, Ship_id, Cust_id to convert to int later
agg = join_4.groupby(
    ['Product_Sub_Category', 'Order_Date'],
    dropna=False,
    as_index=False
).agg({
    'Sales': 'sum',
    'Ord_id': 'min',
    'Prod_id': 'min',
    'Ship_id': 'min',
    'Cust_id': 'min'
})

# Convert ID columns from string IDs to integers by extracting digits
agg['Ord_id'] = agg['Ord_id'].str.extract(r'(\d+)').astype(int)
agg['Prod_id'] = agg['Prod_id'].str.extract(r'(\d+)').astype(int)
agg['Ship_id'] = agg['Ship_id'].str.extract(r'(\d+)').astype(int)
agg['Cust_id'] = agg['Cust_id'].str.extract(r'(\d+)').astype(int)

# Round Sales to int
agg['Sales'] = agg['Sales'].round().astype(int)

# Reorder columns to match target schema
agg = agg[['Product_Sub_Category', 'Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)