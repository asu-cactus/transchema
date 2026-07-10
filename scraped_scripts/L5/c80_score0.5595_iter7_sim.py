import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

grouped = df0.groupby(
    ['Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Item Name'],
    as_index=False
).agg(
    Purchase_ID_x=('Price', 'count'),
    Price_x=('Price', 'sum'),
    Price_y=('Price', 'mean')
)

grouped['Purchase ID_x'] = grouped['Purchase_ID_x'].astype(int)
grouped['Purchase ID_y'] = grouped['Purchase_ID_x'].astype(int)
grouped['Purchase ID'] = grouped['Purchase ID'].astype(int)
grouped['SN'] = grouped['SN'].astype(str)
grouped['Age'] = grouped['Age'].astype(int)
grouped['Age_x'] = grouped['Age']
grouped['Age_y'] = grouped['Age']
grouped['Gender'] = grouped['Gender'].astype(str)
grouped['Item ID'] = grouped['Item ID'].astype(int)
grouped['Item ID_x'] = grouped['Item ID']
grouped['Item ID_y'] = grouped['Item ID']
grouped['Item Name'] = grouped['Item Name'].astype(str)
grouped['Purchase ID_x'] = grouped['Purchase ID_x'].astype(int)
grouped['Purchase ID_y'] = grouped['Purchase ID_y'].astype(int)

result = grouped.rename(columns={
    'Purchase ID': 'Purchase ID',
    'SN': 'SN',
    'Age': 'Age',
    'Gender': 'Gender',
    'Item ID': 'Item ID',
    'Item Name': 'Item Name',
    'Purchase_ID_x': 'Purchase ID_x',
    'Price_x': 'Price_x',
    'Price_y': 'Price_y'
})

# Reorder columns to match target schema exactly
result = result[
    ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
     'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
     'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)