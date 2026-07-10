import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

# Join Source4 (fact) with Source0 on Ord_id to get Order_Date
df = pd.merge(s4, s0[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

# Join with Source1 on Ship_id
df = pd.merge(df, s1[['Ship_id']], on='Ship_id', how='inner')

# Join with Source2 on Cust_id
df = pd.merge(df, s2[['Cust_id']], on='Cust_id', how='inner')

# Join with Source3 on Prod_id
df = pd.merge(df, s3[['Prod_id']], on='Prod_id', how='inner')

# Convert IDs to integers by extracting numeric part after underscore
def extract_int_id(series):
    return series.str.extract(r'_(\d+)$').astype(int)

df['Ord_id'] = extract_int_id(df['Ord_id'])
df['Prod_id'] = extract_int_id(df['Prod_id'])
df['Ship_id'] = extract_int_id(df['Ship_id'])
df['Cust_id'] = extract_int_id(df['Cust_id'])

# Convert Sales and Discount to numeric (float), then sum aggregation requires numeric
df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)

# Group by keys and aggregate Sales and Discount by sum
grouped = df.groupby(['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

# Convert Sales and Discount to int as per target schema
grouped['Sales'] = grouped['Sales'].round().astype(int)
grouped['Discount'] = grouped['Discount'].round().astype(int)

# Reorder columns to match target schema exactly
final_df = grouped[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)