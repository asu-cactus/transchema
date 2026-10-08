import pandas as pd
import re

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

# Join df4 with df0 on Ord_id
merged = pd.merge(df4, df0[['Ord_id']], on='Ord_id', how='inner')

# Join with df1 on Cust_id
merged = pd.merge(merged, df1[['Cust_id', 'Customer_Segment']], on='Cust_id', how='inner')

# Join with df2 on Prod_id
merged = pd.merge(merged, df2[['Prod_id']], on='Prod_id', how='inner')

# Join with df3 on Ship_id
merged = pd.merge(merged, df3[['Ship_id']], on='Ship_id', how='inner')

# Function to extract integer from ID strings like 'Ord_1082' -> 1082
def extract_int(s):
    if pd.isna(s):
        return None
    m = re.search(r'(\d+)', str(s))
    return int(m.group(1)) if m else None

# Convert ID columns to integers
merged['Ord_id'] = merged['Ord_id'].map(extract_int)
merged['Prod_id'] = merged['Prod_id'].map(extract_int)
merged['Ship_id'] = merged['Ship_id'].map(extract_int)
merged['Cust_id'] = merged['Cust_id'].map(extract_int)

# Group by all target columns and aggregate count of Sales (or any column)
grouped = merged.groupby(['Customer_Segment', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({'Sales':'count'})

# Drop the aggregation column 'Sales' as it's not in target schema
result = grouped.drop(columns=['Sales'])

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)