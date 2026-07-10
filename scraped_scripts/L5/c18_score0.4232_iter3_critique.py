import pandas as pd
import re

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Join df1 (orders) with df0 (product categories) on Prod_id
df = pd.merge(df1, df0, on='Prod_id', how='inner')

# Join with df2 (order dates/priorities) on Ord_id
df = pd.merge(df, df2, on='Ord_id', how='inner')

# Join with df3 (customer info) on Cust_id
df = pd.merge(df, df3, on='Cust_id', how='inner')

# Join with df4 (shipping info) on Ship_id
df = pd.merge(df, df4, on='Ship_id', how='inner')

# Extract integer IDs from string IDs
def extract_int_id(s):
    if pd.isna(s):
        return pd.NA
    m = re.search(r'(\d+)', s)
    return int(m.group(1)) if m else pd.NA

df['Ord_id'] = df['Ord_id'].map(extract_int_id)
df['Prod_id'] = df['Prod_id'].map(extract_int_id)
df['Ship_id'] = df['Ship_id'].map(extract_int_id)
df['Cust_id'] = df['Cust_id'].map(extract_int_id)

# Convert numeric columns to appropriate types
df['Order_Quantity'] = df['Order_Quantity'].astype('Int64')
df['Sales'] = df['Sales'].round().astype('Int64')

# Group by the leftmost non-float unique columns except aggregated columns
group_cols = ['Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']
agg_dict = {
    'Order_Quantity': 'sum',
    'Sales': 'sum'
}

df_grouped = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
result = df_grouped[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)