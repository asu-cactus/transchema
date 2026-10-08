import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

# Join Source0 and Source1 on Ship_id
join_01 = pd.merge(s0, s1, how='inner', on='Ship_id')

# Join with Source2 on Cust_id
join_012 = pd.merge(join_01, s2, how='inner', on='Cust_id')

# Join with Source3 on Prod_id
join_0123 = pd.merge(join_012, s3, how='inner', on='Prod_id')

# Join with Source4 on Ord_id
join_all = pd.merge(join_0123, s4, how='inner', on='Ord_id')

# Convert Ord_id, Ship_id, Cust_id to integers by removing prefixes
join_all['Ord_id'] = join_all['Ord_id'].str.replace('Ord_', '', regex=False).astype(int)
join_all['Ship_id'] = join_all['Ship_id'].str.replace('SHP_', '', regex=False).astype(int)
join_all['Cust_id'] = join_all['Cust_id'].str.replace('Cust_', '', regex=False).astype(int)

# Convert Sales to integer by rounding
join_all['Sales'] = join_all['Sales'].round().astype(int)

# Convert Discount to integer percentage
join_all['Discount'] = (join_all['Discount'] * 100).round().astype(int)

# Group by Prod_id, Order_Priority, Ord_id and aggregate sums on Ship_id, Cust_id, Sales, Discount
result = join_all.groupby(['Prod_id', 'Order_Priority', 'Ord_id'], as_index=False).agg({
    'Ship_id': 'sum',
    'Cust_id': 'sum',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Reorder columns to match target schema
result = result[['Prod_id', 'Order_Priority', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)