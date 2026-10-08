import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

# Define aggregation functions
agg_dict = {
    'Purchase ID': 'count',               # Purchase Count
    'SN': pd.Series.nunique,              # SN count distinct
    'Age': 'mean',                       # Age average
    'Item ID': pd.Series.nunique,         # Item ID count distinct
    'Item Name': pd.Series.nunique,       # Item Name count distinct
    'Price': ['mean', 'sum']              # Average Purchase Price, Total Purchase Value
}

grouped = df0.groupby('Gender').agg(agg_dict)

# Flatten MultiIndex columns
grouped.columns = ['Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Average Purchase Price', 'Total Purchase Value']

# Convert types according to target schema
grouped['Purchase Count'] = grouped['Purchase Count'].astype(int)
grouped['SN'] = grouped['SN'].astype(int)
grouped['Age_x'] = grouped['Age_x'].round().astype(int)
grouped['Item ID_x'] = grouped['Item ID_x'].astype(int)
grouped['Item Name'] = grouped['Item Name'].astype(int)
grouped['Average Purchase Price'] = grouped['Average Purchase Price'].astype(float)
grouped['Total Purchase Value'] = grouped['Total Purchase Value'].astype(float)

# For columns with suffixes _x, _y and others in target schema, since only one source table exists,
# we replicate or map columns accordingly.

# Create columns to match target schema:
# 'Price' column in target schema is integer, we can use rounded average price
grouped['Price'] = grouped['Average Purchase Price'].round().astype(int)

# 'Purchase ID_x' (float) - use Purchase Count as float
grouped['Purchase ID_x'] = grouped['Purchase Count'].astype(float)

# 'Age_y' (float) - use Age_x as float
grouped['Age_y'] = grouped['Age_x'].astype(float)

# 'Item ID_y' (float) - use Item ID_x as float
grouped['Item ID_y'] = grouped['Item ID_x'].astype(float)

# 'Purchase ID_y' (integer) - same as Purchase Count
grouped['Purchase ID_y'] = grouped['Purchase Count']

# 'Age' (integer) - same as Age_x
grouped['Age'] = grouped['Age_x']

# 'Item ID' (integer) - same as Item ID_x
grouped['Item ID'] = grouped['Item ID_x']

# Reorder columns to match target schema exactly
result = grouped.reset_index()[[
    'Gender',
    'Purchase Count',
    'SN',
    'Age_x',
    'Item ID_x',
    'Item Name',
    'Price',
    'Purchase ID_x',
    'Age_y',
    'Item ID_y',
    'Average Purchase Price',
    'Purchase ID_y',
    'Age',
    'Item ID',
    'Total Purchase Value'
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)