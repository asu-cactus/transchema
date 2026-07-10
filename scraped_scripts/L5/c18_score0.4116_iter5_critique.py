import pandas as pd
import re

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Join all sources on keys
df = pd.merge(source1, source0[['Prod_id']], on='Prod_id', how='inner')
df = pd.merge(df, source3[['Cust_id', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']], on='Cust_id', how='inner')
df = pd.merge(df, source4[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')
df = pd.merge(df, source2[['Ord_id', 'Order_Date', 'Order_Priority']], on='Ord_id', how='inner')

# Extract numeric part of IDs to convert to integer as per target schema
def extract_num(s):
    # Extract digits from string like 'Ord_1002' -> 1002
    return s.str.extract('(\d+)$').astype(int)

df['Ord_id'] = extract_num(df['Ord_id'])
df['Prod_id'] = extract_num(df['Prod_id'])
df['Ship_id'] = extract_num(df['Ship_id'])
df['Cust_id'] = extract_num(df['Cust_id'])

# Group by leftmost key columns and Ship_Mode (string)
agg = df.groupby(['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Ship_Mode'], as_index=False).agg({
    'Order_Quantity': 'sum',
    'Sales': 'sum'
})

# Convert to int as per target schema
agg['Order_Quantity'] = agg['Order_Quantity'].astype(int)
agg['Sales'] = agg['Sales'].round().astype(int)

# Reorder columns to match target schema
agg = agg[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)