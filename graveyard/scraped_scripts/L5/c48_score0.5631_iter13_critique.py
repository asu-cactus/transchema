import pandas as pd
import re

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

# Join dimension tables to fact table s4
df = s4.merge(s0[['Ord_id', 'Order_Date']], on='Ord_id', how='left')
df = df.merge(s1[['Ship_id']], on='Ship_id', how='left')
df = df.merge(s2[['Cust_id']], on='Cust_id', how='left')
df = df.merge(s3[['Prod_id']], on='Prod_id', how='left')

# Function to extract integer from ID strings like 'Ord_1' -> 1
def extract_int_id(x):
    if pd.isna(x):
        return pd.NA
    m = re.search(r'(\d+)', str(x))
    return int(m.group(1)) if m else pd.NA

# Convert IDs to integers
df['Ord_id'] = df['Ord_id'].map(extract_int_id).astype('Int64')
df['Prod_id'] = df['Prod_id'].map(extract_int_id).astype('Int64')
df['Ship_id'] = df['Ship_id'].map(extract_int_id).astype('Int64')
df['Cust_id'] = df['Cust_id'].map(extract_int_id).astype('Int64')

# Group by Ord_id only, aggregate Sales and Discount by mean
agg_df = df.groupby('Ord_id', as_index=False).agg({
    'Order_Date': 'first',  # Order_Date is same per Ord_id, so take first
    'Prod_id': 'first',     # Assuming Prod_id unique per Ord_id
    'Ship_id': 'first',     # Assuming Ship_id unique per Ord_id
    'Cust_id': 'first',     # Assuming Cust_id unique per Ord_id
    'Sales': 'mean',
    'Discount': 'mean'
})

# Round Sales and Discount to integers as per target schema
agg_df['Sales'] = agg_df['Sales'].round().astype('Int64')
agg_df['Discount'] = agg_df['Discount'].round().astype('Int64')

# Reorder columns to match target schema
result = agg_df[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)