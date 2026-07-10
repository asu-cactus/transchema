import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

# Convert columns to appropriate types
df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce').astype('Int64')
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').astype('Int64')
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce').astype('Int64')
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce')

# Encode SN (string) to integer codes to match target schema
df0['SN'], sn_index = pd.factorize(df0['SN'])
df0['SN'] = df0['SN'].astype('Int64')

# Encode Gender (string) to integer codes to match target schema
df0['Gender'], gender_index = pd.factorize(df0['Gender'])
df0['Gender'] = df0['Gender'].astype('Int64')

# Group by the leftmost columns of target schema (string or int, unique)
group_cols = ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID']

# Aggregation 1: count of Price (integer)
agg_count = df0.groupby(group_cols, dropna=False).agg(Price_x=('Price', 'count')).reset_index()

# Aggregation 2: min of Price (float)
agg_min = df0.groupby(group_cols, dropna=False).agg(Price_y=('Price', 'min')).reset_index()

# Join the two aggregated tables on the group by keys
merged = pd.merge(agg_count, agg_min, on=group_cols, how='inner')

# According to target schema, we need to add duplicated columns with suffixes _x and _y for Purchase ID, Age, Item ID, etc.

# Add duplicated columns with suffix _x (Purchase ID_x, Age_x, Item ID_x)
merged['Purchase ID_x'] = merged['Purchase ID']
merged['Age_x'] = merged['Age']
merged['Item ID_x'] = merged['Item ID']

# Add duplicated columns with suffix _y (Purchase ID_y, Age_y, Item ID_y)
merged['Purchase ID_y'] = merged['Purchase ID']
merged['Age_y'] = merged['Age']
merged['Item ID_y'] = merged['Item ID']

# Reorder columns to match target schema exactly:
# ['Item Name': string, 'Purchase ID': integer, 'SN': integer, 'Age': integer, 'Gender': integer,
#  'Item ID': integer, 'Price_x': integer, 'Purchase ID_x': integer, 'Age_x': integer, 'Item ID_x': integer,
#  'Price_y': float, 'Item ID_y': integer, 'Purchase ID_y': integer, 'Age_y': integer]

result = merged[['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
                 'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
                 'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']]

# Ensure types match target schema
result['Purchase ID'] = result['Purchase ID'].astype('Int64')
result['SN'] = result['SN'].astype('Int64')
result['Age'] = result['Age'].astype('Int64')
result['Gender'] = result['Gender'].astype('Int64')
result['Item ID'] = result['Item ID'].astype('Int64')

result['Price_x'] = result['Price_x'].astype('Int64')
result['Purchase ID_x'] = result['Purchase ID_x'].astype('Int64')
result['Age_x'] = result['Age_x'].astype('Int64')
result['Item ID_x'] = result['Item ID_x'].astype('Int64')

result['Price_y'] = result['Price_y'].astype(float)
result['Item ID_y'] = result['Item ID_y'].astype('Int64')
result['Purchase ID_y'] = result['Purchase ID_y'].astype('Int64')
result['Age_y'] = result['Age_y'].astype('Int64')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)