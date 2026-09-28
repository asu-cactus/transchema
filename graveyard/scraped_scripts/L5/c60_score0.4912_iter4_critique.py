import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

df = df0.copy()

# Convert SN and Gender to categorical codes to get integer representation matching target schema
df['SN'] = df['SN'].astype('category').cat.codes
df['Gender'] = df['Gender'].astype('category').cat.codes

# Group by SN and Gender (leftmost non-float unique attributes)
agg_df = df.groupby(['SN', 'Gender']).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Age_x=('Age', 'min'),
    Age_y=('Age', 'max'),
    Item_ID_x=('Item ID', 'min'),
    Item_ID_y=('Item ID', 'max'),
    Average_Purchase_Price=('Price', 'mean'),
    Purchase_ID_y=('Purchase ID', 'max'),
    Age=('Age', 'sum'),
    Item_ID=('Item ID', 'sum'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

# The target schema also has columns: 'Item Name', 'Price', 'Purchase ID_x', 'Purchase ID_y', 'Age_y', 'Age_x', etc.
# We do not have 'Item Name' aggregation in the plan because it is string and cannot be aggregated meaningfully.
# But target schema has 'Item Name' as integer, so encode it similarly.

# For 'Item Name', take the most frequent value per group (mode), then encode as integer
def mode_encode(series):
    mode_val = series.mode()
    if len(mode_val) > 0:
        return mode_val.iloc[0]
    else:
        return series.iloc[0]

item_name_mode = df.groupby(['SN', 'Gender'])['Item Name'].apply(mode_encode).reset_index()
item_name_mode['Item Name'] = item_name_mode['Item Name'].astype('category').cat.codes

# Merge back to agg_df
agg_df = agg_df.merge(item_name_mode, on=['SN', 'Gender'], how='left')

# For 'Price' and 'Purchase ID_x' columns in target schema:
# 'Price' in target is integer, take min price per group and convert to int
price_min = df.groupby(['SN', 'Gender'])['Price'].min().reset_index()
price_min.rename(columns={'Price': 'Price'}, inplace=True)
agg_df = agg_df.merge(price_min, on=['SN', 'Gender'], how='left')

# 'Purchase ID_x' in target is float, take mean Purchase ID per group
purchase_id_mean = df.groupby(['SN', 'Gender'])['Purchase ID'].mean().reset_index()
purchase_id_mean.rename(columns={'Purchase ID': 'Purchase ID_x'}, inplace=True)
agg_df = agg_df.merge(purchase_id_mean, on=['SN', 'Gender'], how='left')

# Rename columns to match target schema exactly
agg_df.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'SN': 'SN',
    'Age_x': 'Age_x',
    'Gender': 'Gender',
    'Item_ID_x': 'Item ID_x',
    'Item Name': 'Item Name',
    'Price': 'Price',
    'Purchase_ID_x': 'Purchase ID_x',
    'Age_y': 'Age_y',
    'Item_ID_y': 'Item ID_y',
    'Average_Purchase_Price': 'Average Purchase Price',
    'Purchase_ID_y': 'Purchase ID_y',
    'Age': 'Age',
    'Item_ID': 'Item ID',
    'Total_Purchase_Value': 'Total Purchase Value'
}, inplace=True)

# Convert types to match target schema
agg_df['Purchase Count'] = agg_df['Purchase Count'].astype(int)
agg_df['SN'] = agg_df['SN'].astype(int)
agg_df['Age_x'] = agg_df['Age_x'].astype(int)
agg_df['Gender'] = agg_df['Gender'].astype(int)
agg_df['Item ID_x'] = agg_df['Item ID_x'].astype(int)
agg_df['Item Name'] = agg_df['Item Name'].astype(int)
agg_df['Price'] = agg_df['Price'].astype(int)
agg_df['Purchase ID_x'] = agg_df['Purchase ID_x'].astype(float)
agg_df['Age_y'] = agg_df['Age_y'].astype(int)
agg_df['Item ID_y'] = agg_df['Item ID_y'].astype(int)
agg_df['Average Purchase Price'] = agg_df['Average Purchase Price'].astype(float)
agg_df['Purchase ID_y'] = agg_df['Purchase ID_y'].astype(int)
agg_df['Age'] = agg_df['Age'].astype(int)
agg_df['Item ID'] = agg_df['Item ID'].astype(int)
agg_df['Total Purchase Value'] = agg_df['Total Purchase Value'].astype(float)

# Save to target file
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)