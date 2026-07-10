import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join source4 with source0 on Prod_id to get Product_Sub_Category
merged = pd.merge(source4, source0[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='inner')

# Join with source1 on Cust_id
merged = pd.merge(merged, source1[['Cust_id']], on='Cust_id', how='inner')

# Join with source2 on Ord_id
merged = pd.merge(merged, source2[['Ord_id']], on='Ord_id', how='inner')

# Join with source3 on Ship_id
merged = pd.merge(merged, source3[['Ship_id']], on='Ship_id', how='inner')

# Multiply Discount by 100 before aggregation
merged['Discount'] = merged['Discount'] * 100

# Group by keys and aggregate sums
agg_df = merged.groupby(
    ['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'],
    as_index=False
).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Round and convert types as required
agg_df['Order_Quantity'] = agg_df['Order_Quantity'].astype('Int64')
agg_df['Sales'] = agg_df['Sales'].round().astype('Int64')
agg_df['Discount'] = agg_df['Discount'].round().astype('Int64')

# Reorder columns to match target schema
result = agg_df[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)