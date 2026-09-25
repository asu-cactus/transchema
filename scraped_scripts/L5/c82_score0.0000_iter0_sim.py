import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

df0['Gender'] = df0['Gender'].map({'Male': 1, 'Female': 2}).fillna(0).astype(int)

agg = df0.groupby('Item Name').agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum'),
    Purchase_ID_sum=('Purchase ID', 'sum'),
    Age_sum=('Age', 'sum'),
    Item_ID_sum=('Item ID', 'sum'),
    SN_count=('SN', 'count')
).reset_index()

agg = agg.rename(columns={
    'Item Name': 'Item Name',
    'Purchase_Count': 'Purchase Count',
    'Total_Purchase_Value': 'Total Purchase Value'
})

# To create the multiple columns with suffixes _x and _y and the original columns as in target schema,
# we need to join the aggregated data back to the original data on 'Item Name' to get the other columns.

# Join agg with original df0 on 'Item Name' to get columns for _x and _y suffixes and original columns
merged = pd.merge(df0, agg, on='Item Name', how='inner', suffixes=('_x', '_y'))

# Now select and rename columns to match target schema:
# Target schema: ['Item ID': int, 'Item Name': str, 'Purchase ID_x': int, 'SN': int, 'Age_x': int, 'Gender': int,
# 'Purchase Count': int, 'Purchase ID_y': float, 'Age_y': float, 'Item Price': float, 'Purchase ID': int, 'Age': int, 'Total Purchase Value': float]

# 'Purchase ID_x' from original df0 'Purchase ID'
# 'SN' from original df0 'SN' but SN is string in source, target shows int, so convert SN to int if possible, else assign NaN
# 'Age_x' from original df0 'Age'
# 'Gender' from original df0 'Gender' (already mapped)
# 'Purchase Count' from agg
# 'Purchase ID_y' from agg 'Purchase_ID_sum' (float)
# 'Age_y' from agg 'Age_sum' (float)
# 'Item Price' from original df0 'Price'
# 'Purchase ID' from original df0 'Purchase ID'
# 'Age' from original df0 'Age'
# 'Total Purchase Value' from agg

# Convert SN to integer if possible, else NaN
def try_int(x):
    try:
        return int(''.join(filter(str.isdigit, str(x))))
    except:
        return pd.NA

merged['SN'] = merged['SN'].apply(try_int)

result = pd.DataFrame({
    'Item ID': merged['Item ID'].astype(int),
    'Item Name': merged['Item Name'],
    'Purchase ID_x': merged['Purchase ID_x'].astype(int),
    'SN': merged['SN'],
    'Age_x': merged['Age_x'].astype(int),
    'Gender': merged['Gender'].astype(int),
    'Purchase Count': merged['Purchase Count'].astype(int),
    'Purchase ID_y': merged['Purchase_ID_sum'].astype(float),
    'Age_y': merged['Age_sum'].astype(float),
    'Item Price': merged['Price'].astype(float),
    'Purchase ID': merged['Purchase ID'].astype(int),
    'Age': merged['Age'].astype(int),
    'Total Purchase Value': merged['Total Purchase Value'].astype(float)
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)