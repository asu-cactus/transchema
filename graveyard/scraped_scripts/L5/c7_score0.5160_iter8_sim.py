import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

s0['Prod_id'] = s0['Prod_id'].astype(str)
s4['Prod_id'] = s4['Prod_id'].astype(str)
s4['Ord_id'] = s4['Ord_id'].astype(str)
s4['Ship_id'] = s4['Ship_id'].astype(str)
s4['Cust_id'] = s4['Cust_id'].astype(str)

grouped = s4.groupby('Prod_id', as_index=False).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum',
    'Discount': 'sum'
})

# We need Product_Sub_Category from s0, join on Prod_id
merged = pd.merge(s0[['Prod_id', 'Product_Sub_Category']], grouped, on='Prod_id', how='inner')

# The target requires Ord_id, Prod_id, Ship_id, Cust_id, Sales, Discount, Order_Quantity, Product_Sub_Category
# s4 has Ord_id, Ship_id, Cust_id, Sales, Discount, Order_Quantity, Prod_id
# We have Product_Sub_Category from s0

# Join s4 with s0 on Prod_id to get Product_Sub_Category for each row in s4
merged_full = pd.merge(s4, s0[['Prod_id', 'Product_Sub_Category']], on='Prod_id', how='left')

# Select and reorder columns as per target schema
result = merged_full[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Convert numeric columns to integer as target schema requires integer types
for col in ['Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']:
    if col in ['Order_Quantity', 'Sales', 'Discount']:
        result[col] = result[col].fillna(0).round().astype(int)
    else:
        # Ord_id, Prod_id, Ship_id, Cust_id are strings, keep as is
        pass

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)