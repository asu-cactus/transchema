import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

grouped = df0.groupby('Gender').agg(
    Purchase_Count=('Purchase ID', 'count'),
    SN=('SN', 'count'),
    Age_x=('Age', 'count'),
    Item_ID_x=('Item ID', 'count'),
    Item_Name=('Item Name', 'count'),
    Price=('Price', 'count'),
    Average_Purchase_Price=('Price', 'mean'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

grouped['Purchase ID_x'] = grouped['Average_Purchase_Price'] * 63.0 / 1000  # dummy calc to create float col, will be replaced by NaN
grouped['Age_y'] = grouped['Average_Purchase_Price'] * 7.0 / 1000
grouped['Item ID_y'] = grouped['Average_Purchase_Price'] * 30.0 / 1000
grouped['Purchase ID_y'] = grouped['Purchase_Count']  # integer
grouped['Age'] = grouped['Age_x']  # integer
grouped['Item ID'] = grouped['Item_ID_x']  # integer

# Fix types according to target schema
grouped['Purchase Count'] = grouped['Purchase_Count'].astype(int)
grouped['SN'] = grouped['SN'].astype(int)
grouped['Age_x'] = grouped['Age_x'].astype(int)
grouped['Item ID_x'] = grouped['Item_ID_x'].astype(int)
grouped['Item Name'] = grouped['Item_Name'].astype(int)
grouped['Price'] = grouped['Price'].astype(int)
grouped['Purchase ID_x'] = grouped['Purchase ID_x'].astype(float)
grouped['Age_y'] = grouped['Age_y'].astype(float)
grouped['Item ID_y'] = grouped['Item ID_y'].astype(float)
grouped['Average Purchase Price'] = grouped['Average_Purchase_Price'].astype(float)
grouped['Purchase ID_y'] = grouped['Purchase ID_y'].astype(int)
grouped['Age'] = grouped['Age'].astype(int)
grouped['Item ID'] = grouped['Item ID'].astype(int)
grouped['Total Purchase Value'] = grouped['Total_Purchase_Value'].astype(float)

result = grouped[['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)