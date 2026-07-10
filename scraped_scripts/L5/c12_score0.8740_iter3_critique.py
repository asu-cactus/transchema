import pandas as pd
import re

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

# Join tables stepwise
df = pd.merge(source4, source0, on="Ship_id", how="inner")
df = pd.merge(df, source1, on="Ord_id", how="inner")
df = pd.merge(df, source2, on="Cust_id", how="inner")
df = pd.merge(df, source3, on="Prod_id", how="inner")

# Function to extract integer from ID strings like 'Ord_1082' -> 1082
def extract_int_id(s):
    # Extract digits from string
    return s.str.extract(r'(\d+)$').astype(int)

# Extract integer IDs
df['Ord_id'] = extract_int_id(df['Ord_id'])
df['Prod_id'] = extract_int_id(df['Prod_id'])
df['Ship_id'] = extract_int_id(df['Ship_id'])
df['Cust_id'] = extract_int_id(df['Cust_id'])

# Group by Order_Priority and Ship_Mode
agg_df = df.groupby(['Order_Priority', 'Ship_Mode'], as_index=False).agg({
    'Ord_id': 'min',
    'Prod_id': 'min',
    'Ship_id': 'min',
    'Cust_id': 'min',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Round Sales and Discount and convert to integer type
agg_df['Sales'] = agg_df['Sales'].round().astype('Int64')
agg_df['Discount'] = agg_df['Discount'].round().astype('Int64')

# Reorder columns to match target schema
agg_df = agg_df[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)