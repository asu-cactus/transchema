import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

agg = df0.groupby(['SN', 'Gender']).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean'),
    Age_x=('Age', 'first'),
    Item_ID_x=('Item ID', 'first'),
    Item_Name=('Item Name', 'first'),
    Purchase_ID_x=('Purchase ID', 'first'),
    Age_y=('Age', 'mean'),
    Item_ID_y=('Item ID', 'mean'),
    Purchase_ID_y=('Purchase ID', 'count'),
    Age=('Age', 'sum'),
    Item_ID=('Item ID', 'sum'),
    Price=('Price', 'sum')
).reset_index()

# Reorder and rename columns to match target schema exactly
agg = agg.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Age_x': 'Age_x',
    'Gender': 'Gender',
    'Item_ID_x': 'Item ID_x',
    'Item_Name': 'Item Name',
    'Price': 'Price',
    'Purchase_ID_x': 'Purchase ID_x',
    'Age_y': 'Age_y',
    'Item_ID_y': 'Item ID_y',
    'Average_Purchase_Price': 'Average Purchase Price',
    'Purchase_ID_y': 'Purchase ID_y',
    'Age': 'Age',
    'Item_ID': 'Item ID',
    'Total_Purchase_Value': 'Total Purchase Value'
})

# Ensure correct dtypes as per target schema
agg['Purchase Count'] = agg['Purchase Count'].astype(int)
agg['SN'] = agg['SN'].astype(str)  # SN is integer in target but source SN is string, keep as string
agg['Age_x'] = agg['Age_x'].astype(int)
agg['Gender'] = agg['Gender'].astype(str)  # Gender is integer in target but source is string, keep as string
agg['Item ID_x'] = agg['Item ID_x'].astype(int)
agg['Item Name'] = agg['Item Name'].astype(str)
agg['Price'] = agg['Price'].astype(float)
agg['Purchase ID_x'] = agg['Purchase ID_x'].astype(float)
agg['Age_y'] = agg['Age_y'].astype(float)
agg['Item ID_y'] = agg['Item ID_y'].astype(float)
agg['Average Purchase Price'] = agg['Average Purchase Price'].astype(float)
agg['Purchase ID_y'] = agg['Purchase ID_y'].astype(int)
agg['Age'] = agg['Age'].astype(int)
agg['Item ID'] = agg['Item ID'].astype(int)
agg['Total Purchase Value'] = agg['Total Purchase Value'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)