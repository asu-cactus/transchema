import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join Source5_7_4 with Source5_7_0 on Prod_id
join_1 = pd.merge(source4, source0, how='inner', on='Prod_id')

# Join with Source5_7_1 on Cust_id
join_2 = pd.merge(join_1, source1, how='inner', on='Cust_id')

# Join with Source5_7_2 on Ord_id
join_3 = pd.merge(join_2, source2, how='inner', on='Ord_id')

# Join with Source5_7_3 on Ship_id
join_4 = pd.merge(join_3, source3, how='inner', on='Ship_id')

# Group by key columns and aggregate measures
grouped = join_4.groupby(
    ['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'],
    as_index=False
).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum',
    'Discount': 'mean'
})

# Round and convert Discount to integer percentage
grouped['Discount'] = (grouped['Discount'] * 100).round().astype(int)

# Cast Order_Quantity and Sales to int
grouped['Order_Quantity'] = grouped['Order_Quantity'].astype(int)
grouped['Sales'] = grouped['Sales'].round().astype(int)

# Cast key columns to string (except Order_Quantity, Sales, Discount already handled)
grouped['Ord_id'] = grouped['Ord_id'].astype(str)
grouped['Prod_id'] = grouped['Prod_id'].astype(str)
grouped['Ship_id'] = grouped['Ship_id'].astype(str)
grouped['Cust_id'] = grouped['Cust_id'].astype(str)
grouped['Product_Sub_Category'] = grouped['Product_Sub_Category'].astype(str)

# Reorder columns to match target schema exactly
result = grouped[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)