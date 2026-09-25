import pandas as pd

# Read sources with index_col=0 to ignore the first index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_78/training_2.csv", index_col=0)

# Join source0 with source1 on Prod_id (product dimension)
merged_1 = pd.merge(source0, source1, how='left', on='Prod_id')

# Join the above result with source2 on Cust_id (customer dimension)
merged_2 = pd.merge(merged_1, source2, how='left', on='Cust_id')

# Define group by keys (leftmost string columns uniquely identifying rows)
group_by_cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

# Define aggregation columns (numeric columns to sum)
agg_cols = ['Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin']

# Aggregate by sum on numeric columns, group by the keys
result = merged_2.groupby(group_by_cols, as_index=False)[agg_cols].sum()

# After aggregation, add back the non-numeric columns from the dimension tables
# These columns are unique per Prod_id or Cust_id, so we can merge them back safely

# Extract unique product info from source1
product_info = source1.drop_duplicates(subset=['Prod_id'])
# Extract unique customer info from source2
customer_info = source2.drop_duplicates(subset=['Cust_id'])

# Merge product info back
result = pd.merge(result, product_info, how='left', on='Prod_id')
# Merge customer info back
result = pd.merge(result, customer_info, how='left', on='Cust_id')

# Reorder columns to match target schema exactly
cols = ['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount', 'Order_Quantity', 'Profit', 'Shipping_Cost', 'Product_Base_Margin',
        'Product_Category', 'Product_Sub_Category', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']

result = result[cols]

# Cast columns to correct types
result['Order_Quantity'] = result['Order_Quantity'].astype('Int64')
result['Sales'] = result['Sales'].astype(float)
result['Discount'] = result['Discount'].astype(float)
result['Profit'] = result['Profit'].astype(float)
result['Shipping_Cost'] = result['Shipping_Cost'].astype(float)
result['Product_Base_Margin'] = pd.to_numeric(result['Product_Base_Margin'], errors='coerce')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_78/target_multisource_mcts.csv", index=False)