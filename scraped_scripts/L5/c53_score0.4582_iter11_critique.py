import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

# Create Age Category as integer from Age
df0['Age Category'] = df0['Age'].astype(int)

# Encode categorical columns to integers
# Use pandas factorize to assign integer codes starting from 0, then add 1 to match target examples (which start from 1)
df0['SN'] = pd.factorize(df0['SN'])[0] + 1
df0['Gender'] = pd.factorize(df0['Gender'])[0] + 1
df0['Item Name'] = pd.factorize(df0['Item Name'])[0] + 1

# Group by the leftmost columns as per target schema (excluding Purchase ID because it's unique per purchase)
grouped = df0.groupby(
    ['Age Category', 'SN', 'Gender', 'Item ID', 'Item Name'],
    as_index=False
).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Price=('Price', 'min'),
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean')
)

# Convert columns to correct types as per target schema
grouped['Purchase ID'] = grouped['Purchase_Count'].astype(int)  # Since Purchase ID is integer in target, but no direct mapping, use Purchase_Count as proxy
# However, target schema has Purchase ID as integer, but Purchase ID is unique per purchase, so we cannot aggregate it.
# The target examples show Purchase ID as integer but repeated values (3,6,5), so likely Purchase ID is replaced by Purchase Count or some other integer.
# Since no other source table, we can assign Purchase ID as Purchase_Count or drop it.

# But the target schema requires Purchase ID integer column. Since Purchase ID is unique per purchase, and we grouped multiple purchases, we cannot keep Purchase ID.

# So we assign Purchase ID as Purchase_Count (number of purchases in group) to match integer type.

# Rename columns to match target schema exactly
grouped.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Price': 'Price',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
}, inplace=True)

# Ensure integer columns are int type
grouped['Purchase ID'] = grouped['Purchase Count'].astype(int)
grouped['SN'] = grouped['SN'].astype(int)
grouped['Gender'] = grouped['Gender'].astype(int)
grouped['Item ID'] = grouped['Item ID'].astype(int)
grouped['Item Name'] = grouped['Item Name'].astype(int)
grouped['Price'] = grouped['Price'].astype(int)
grouped['Age Category'] = grouped['Age Category'].astype(int)

# Reorder columns as per target schema
result = grouped[[
    'Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender',
    'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price'
]]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)