import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_84/training_0.csv", index_col=0)

# Encode SN, Gender, Item Name to integer codes
df0['SN_code'] = pd.factorize(df0['SN'])[0]
df0['Gender_code'] = pd.factorize(df0['Gender'])[0]
df0['Item_Name_code'] = pd.factorize(df0['Item Name'])[0]

grouped = df0.groupby(
    ['SN_code', 'Age', 'Gender_code', 'Item ID', 'Item_Name_code'],
    as_index=False
).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Average_Purchase_Price=('Price', 'mean'),
    Total_Purchase_Value=('Price', 'sum'),
    Purchase_ID_x=('Purchase ID', 'mean'),
    Purchase_ID_y=('Purchase ID', 'max'),
    Price=('Price', 'mean')  # to get Price as integer later
)

# Rename columns to match target schema
grouped.rename(columns={
    'SN_code': 'SN',
    'Gender_code': 'Gender',
    'Item_Name_code': 'Item Name',
    'Purchase_ID_x': 'Purchase ID_x',
    'Purchase_ID_y': 'Purchase ID_y',
    'Price': 'Price',
}, inplace=True)

# Create Age_x, Age_y, Age columns
grouped['Age_x'] = grouped['Age'].astype(int)
grouped['Age_y'] = grouped['Age_x'].astype(float)
grouped['Age'] = grouped['Age_x'].astype(int)

# Create Item ID_x, Item ID_y, Item ID columns
grouped['Item ID_x'] = grouped['Item ID'].astype(int)
grouped['Item ID_y'] = grouped['Item ID_x'].astype(float)
grouped['Item ID'] = grouped['Item ID_x'].astype(int)

# Convert SN, Gender, Item Name to int
grouped['SN'] = grouped['SN'].astype(int)
grouped['Gender'] = grouped['Gender'].astype(int)
grouped['Item Name'] = grouped['Item Name'].astype(int)

# Convert Price to int as in target schema
grouped['Price'] = grouped['Price'].round().astype(int)

# Convert Purchase ID_x to float (already mean)
grouped['Purchase ID_x'] = grouped['Purchase ID_x'].astype(float)

# Purchase ID_y is max, convert to int
grouped['Purchase ID_y'] = grouped['Purchase ID_y'].astype(int)

# Reorder columns exactly as target schema
cols = [
    'Purchase_Count', 'SN', 'Age_x', 'Gender', 'Item ID_x', 'Item Name', 'Price',
    'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average_Purchase_Price', 'Purchase ID_y',
    'Age', 'Item ID', 'Total_Purchase_Value'
]

result = grouped[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_84/target_multisource_mcts.csv", index=False)