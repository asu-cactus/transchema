import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

df['Age Category'] = df['Age'].astype(int)

grouped = df.groupby('Age Category').agg(
    Purchase_ID=('Purchase ID', 'count'),
    SN=('SN', 'count'),
    Purchase_Count=('Purchase ID', 'count'),
    Gender=('Gender', 'count'),
    Item_ID=('Item ID', 'count'),
    Item_Name=('Item Name', 'count'),
    Price=('Price', 'count'),
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean')
).reset_index()

grouped = grouped.rename(columns={
    'Age Category': 'Age Category',
    'Purchase_ID': 'Purchase ID',
    'SN': 'SN',
    'Purchase_Count': 'Purchase Count',
    'Gender': 'Gender',
    'Item_ID': 'Item ID',
    'Item_Name': 'Item Name',
    'Price': 'Price',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

grouped = grouped.astype({
    'Age Category': int,
    'Purchase ID': int,
    'SN': int,
    'Purchase Count': int,
    'Gender': int,
    'Item ID': int,
    'Item Name': int,
    'Price': int,
    'Total Purchase Value': float,
    'Average Purchase Price': float
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)