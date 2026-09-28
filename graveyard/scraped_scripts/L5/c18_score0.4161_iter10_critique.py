import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Join Source1 and Source0 on Prod_id
joined_10 = pd.merge(s1, s0[['Prod_id']], on='Prod_id', how='inner')

# Join with Source2 on Ord_id
joined_20 = pd.merge(joined_10, s2[['Ord_id']], on='Ord_id', how='inner')

# Join with Source3 on Cust_id
joined_30 = pd.merge(joined_20, s3[['Cust_id']], on='Cust_id', how='inner')

# Join with Source4 on Ship_id, also get Ship_Mode
joined_40 = pd.merge(joined_30, s4[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')

# Group by the leftmost key columns of target schema
group_cols = ['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

agg = joined_40.groupby(group_cols, dropna=False, as_index=False).agg({'Sales': 'sum'})

# Convert IDs from string to int by extracting numeric part
def extract_int_id(x, prefix):
    if isinstance(x, str) and x.startswith(prefix):
        return int(x.split('_')[1])
    return pd.NA

agg['Ord_id'] = agg['Ord_id'].apply(lambda x: extract_int_id(x, 'Ord_'))
agg['Prod_id'] = agg['Prod_id'].apply(lambda x: extract_int_id(x, 'Prod_'))
agg['Ship_id'] = agg['Ship_id'].apply(lambda x: extract_int_id(x, 'SHP_'))
agg['Cust_id'] = agg['Cust_id'].apply(lambda x: extract_int_id(x, 'Cust_'))

# Ensure Order_Quantity is int
agg['Order_Quantity'] = agg['Order_Quantity'].astype(int)

# Round Sales and convert to integer type
agg['Sales'] = agg['Sales'].round(0).astype('Int64')

# Reorder columns exactly as target schema
result = agg[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)