import pandas as pd

# Read source data
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

# Derive Age Category by rounding Age
df0['Age Category'] = df0['Age'].round().astype(int)

# Encode categorical columns to integers
df0['SN'] = df0['SN'].astype('category').cat.codes.astype(int)
df0['Gender'] = df0['Gender'].astype('category').cat.codes.astype(int)
df0['Item Name'] = df0['Item Name'].astype('category').cat.codes.astype(int)

# Group by the specified columns
agg = df0.groupby(['Age Category', 'Purchase ID', 'SN', 'Gender', 'Item ID', 'Item Name']).agg(
    Purchase_ID = ('Purchase ID', 'count'),
    SN_count = ('SN', 'count'),
    Item_ID_count = ('Item ID', 'count'),
    Item_Name_count = ('Item Name', 'count'),
    Price_count = ('Price', 'count'),
    Total_Purchase_Value = ('Price', 'sum'),
    Average_Purchase_Price = ('Price', 'mean')
).reset_index()

# Rename columns to match target schema exactly
agg = agg.rename(columns={
    'Purchase_ID': 'Purchase Count',
    'SN': 'SN',
    'Gender': 'Gender',
    'Item ID': 'Item ID',
    'Item Name': 'Item Name',
    'Price_count': 'Price'
})

# The columns 'SN', 'Gender', 'Item ID', 'Item Name' are already in groupby and present in agg

# Select and reorder columns exactly as target schema
result = agg[[
    'Age Category',
    'Purchase ID',
    'SN',
    'Purchase Count',
    'Gender',
    'Item ID',
    'Item Name',
    'Price',
    'Total_Purchase_Value',
    'Average_Purchase_Price'
]]

# Rename columns to match target schema exactly (fix underscores)
result = result.rename(columns={
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

# Ensure correct dtypes
result['Age Category'] = result['Age Category'].astype(int)
result['Purchase ID'] = result['Purchase ID'].astype(int)
result['SN'] = result['SN'].astype(int)
result['Purchase Count'] = result['Purchase Count'].astype(int)
result['Gender'] = result['Gender'].astype(int)
result['Item ID'] = result['Item ID'].astype(int)
result['Item Name'] = result['Item Name'].astype(int)
result['Price'] = result['Price'].astype(int)
result['Total Purchase Value'] = result['Total Purchase Value'].astype(float)
result['Average Purchase Price'] = result['Average Purchase Price'].astype(float)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)