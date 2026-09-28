import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Step 1: Union Source5_18_0 to Source5_18_4 is not possible due to different schemas, so skip union of all.

# Instead, join sources stepwise to get all needed columns.

# Join s1 and s0 on Prod_id to bring product info (though product_category not needed in target)
# But target does not need product_category or sub_category, so skip s0 join.

# Join s1 and s4 on Ship_id to get Ship_Mode
df = pd.merge(s1, s4[['Ship_Mode', 'Ship_id']], on='Ship_id', how='left')

# Join with s3 on Cust_id to get customer info (not needed in target, so skip s3 join)

# Join with s2 on Ord_id to get order info (not needed in target, so skip s2 join)

# Select and convert columns to target schema:
# Target schema: ['Order_Quantity': int, 'Ship_Mode': str, 'Ord_id': int, 'Prod_id': int, 'Ship_id': int, 'Cust_id': int, 'Sales': int]

# Convert Ord_id, Prod_id, Ship_id, Cust_id from strings like 'Ord_1082' to integers 1082 etc.
def extract_int(s):
    if pd.isna(s):
        return None
    return int(''.join(filter(str.isdigit, s)))

df['Order_Quantity'] = df['Order_Quantity'].astype(int)
df['Ship_Mode'] = df['Ship_Mode'].astype(str)
df['Ord_id'] = df['Ord_id'].map(extract_int)
df['Prod_id'] = df['Prod_id'].map(extract_int)
df['Ship_id'] = df['Ship_id'].map(extract_int)
df['Cust_id'] = df['Cust_id'].map(extract_int)
df['Sales'] = df['Sales'].round().astype('Int64')

# Group by Order_Quantity and aggregate other columns by first (since target examples show unique rows)
# But target examples show all columns have same values per row, so group by Order_Quantity and take first
result = df.groupby('Order_Quantity', as_index=False).agg({
    'Ship_Mode': 'first',
    'Ord_id': 'first',
    'Prod_id': 'first',
    'Ship_id': 'first',
    'Cust_id': 'first',
    'Sales': 'first'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)