import pandas as pd
import re

def extract_int(s):
    if pd.isna(s):
        return None
    m = re.search(r'(\d+)', str(s))
    return int(m.group(1)) if m else None

# Read source files
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

# Join all source tables on their keys
j0 = pd.merge(src0, src1, how='inner', on='Cust_id')
j1 = pd.merge(j0, src2, how='inner', on='Ship_id')
j2 = pd.merge(j1, src3, how='inner', on='Prod_id')
j3 = pd.merge(j2, src4, how='inner', on='Ord_id')

# Select relevant columns
df = j3[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

# Convert string IDs to integers by extracting numeric parts
df['Ord_id'] = df['Ord_id'].apply(extract_int)
df['Prod_id'] = df['Prod_id'].apply(extract_int)
df['Ship_id'] = df['Ship_id'].apply(extract_int)
df['Cust_id'] = df['Cust_id'].apply(extract_int)

# Group by Order_Priority and Ship_Mode, aggregate sums of other columns
df = df.groupby(['Order_Priority', 'Ship_Mode'], as_index=False).agg({
    'Ord_id': 'sum',
    'Prod_id': 'sum',
    'Ship_id': 'sum',
    'Cust_id': 'sum',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Round Sales and Discount to integers
df['Sales'] = df['Sales'].round().astype('Int64')
df['Discount'] = df['Discount'].round().astype('Int64')

# Ensure Order_Priority and Ship_Mode are strings
df['Order_Priority'] = df['Order_Priority'].astype(str)
df['Ship_Mode'] = df['Ship_Mode'].astype(str)

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)