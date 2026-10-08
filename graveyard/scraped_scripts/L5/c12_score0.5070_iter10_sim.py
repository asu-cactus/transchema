import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

# UNPIVOT step: Source4 has columns Sales, Discount, Order_Quantity, Profit, Shipping_Cost, Product_Base_Margin
# We only need Sales and Discount as per target schema, so unpivot Sales and Discount to rows with a 'Measure' column
# But target schema expects Sales and Discount as columns, so no unpivot needed here actually.
# The partial plan suggests UNPIVOT and PIVOT, but here we can just keep Sales and Discount as is.
# So we skip unpivot and pivot and just join all sources.

# Join s1 (Order_Priority) with s4 on Ord_id
join_1 = pd.merge(s1[['Ord_id', 'Order_Priority']], s4[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']], on='Ord_id', how='inner')

# Join with s0 (Ship_Mode) on Ship_id
join_2 = pd.merge(join_1, s0[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')

# Join with s2 (Customer info) on Cust_id
join_3 = pd.merge(join_2, s2[['Cust_id']], on='Cust_id', how='inner')

# Join with s3 (Product info) on Prod_id
join_4 = pd.merge(join_3, s3[['Prod_id']], on='Prod_id', how='inner')

# Select and reorder columns as per target schema
result = join_4[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Convert Sales and Discount to integer as target schema requires integer
result['Sales'] = result['Sales'].round().astype('Int64')
result['Discount'] = result['Discount'].round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)