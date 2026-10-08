import pandas as pd
import re

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join source4 with source0 on Prod_id to get Product_Sub_Category
join1 = pd.merge(source4, source0[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='inner')

# Join with source1 on Cust_id
join2 = pd.merge(join1, source1[['Cust_id']], on='Cust_id', how='inner')

# Join with source2 on Ord_id
join3 = pd.merge(join2, source2[['Ord_id']], on='Ord_id', how='inner')

# Join with source3 on Ship_id
join4 = pd.merge(join3, source3[['Ship_id']], on='Ship_id', how='inner')

# Extract numeric part from IDs and convert to int
def extract_int_id(s):
    # Extract digits from string like "Ord_1082" -> 1082
    # If already int, just return
    if pd.isna(s):
        return pd.NA
    if isinstance(s, int):
        return s
    match = re.search(r'(\d+)', str(s))
    if match:
        return int(match.group(1))
    else:
        return pd.NA

join4['Ord_id'] = join4['Ord_id'].apply(extract_int_id)
join4['Prod_id'] = join4['Prod_id'].apply(extract_int_id)
join4['Ship_id'] = join4['Ship_id'].apply(extract_int_id)
join4['Cust_id'] = join4['Cust_id'].apply(extract_int_id)

# Convert Discount from fraction to percentage before aggregation
join4['Discount'] = join4['Discount'] * 100

# Group by the keys and sum the measures
grouped = join4.groupby(
    ['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'],
    as_index=False
).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Round and convert to int as per target schema
grouped['Order_Quantity'] = grouped['Order_Quantity'].round().astype(int)
grouped['Sales'] = grouped['Sales'].round().astype(int)
grouped['Discount'] = grouped['Discount'].round().astype(int)

# Reorder columns to match target schema
result = grouped[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)