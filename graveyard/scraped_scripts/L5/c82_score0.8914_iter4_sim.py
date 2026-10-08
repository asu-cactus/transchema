import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

df0['Gender'] = df0['Gender'].map({'Male': 1, 'Female': 2}).fillna(0).astype(int)

grouped = df0.groupby('Item Name').agg(
    Item_ID=('Item ID', 'first'),
    Purchase_ID_x=('Purchase ID', 'count'),
    SN=('SN', 'nunique'),
    Age_x=('Age', 'max'),
    Gender=('Gender', 'max'),
    Purchase_Count=('Purchase ID', 'count'),
    Purchase_ID_y=('Purchase ID', 'mean'),
    Age_y=('Age', 'mean'),
    Item_Price=('Price', 'mean'),
    Purchase_ID=('Purchase ID', 'max'),
    Age=('Age', 'max'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

grouped = grouped.rename(columns={
    'Item_ID': 'Item ID',
    'Item_Price': 'Item Price',
    'Purchase_ID_x': 'Purchase ID_x',
    'Purchase_ID_y': 'Purchase ID_y',
    'Purchase_Count': 'Purchase Count',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Age_x': 'Age_x',
    'Age_y': 'Age_y',
    'Purchase_ID': 'Purchase ID',
    'Age': 'Age',
    'SN': 'SN',
    'Gender': 'Gender',
    'Item Name': 'Item Name'
})

grouped = grouped.astype({
    'Item ID': 'int64',
    'Purchase ID_x': 'int64',
    'SN': 'int64',
    'Age_x': 'int64',
    'Gender': 'int64',
    'Purchase Count': 'int64',
    'Purchase ID_y': 'float64',
    'Age_y': 'float64',
    'Item Price': 'float64',
    'Purchase ID': 'int64',
    'Age': 'int64',
    'Total Purchase Value': 'float64'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)