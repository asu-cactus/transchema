import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_84/training_0.csv", index_col=0)

grouped = df0.groupby(
    ['SN', 'Age', 'Gender', 'Item ID', 'Item Name', 'Price', 'Purchase ID'],
    as_index=False
).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Average_Purchase_Price=('Price', 'mean'),
    Total_Purchase_Value=('Price', 'sum')
)

grouped.rename(columns={
    'Age': 'Age_x',
    'Item ID': 'Item ID_x',
    'Purchase ID': 'Purchase ID_x'
}, inplace=True)

grouped['Age_y'] = grouped['Age_x'].astype(float)
grouped['Item ID_y'] = grouped['Item ID_x'].astype(float)
grouped['Purchase ID_y'] = grouped['Purchase ID_x'].astype(int)
grouped['Age'] = grouped['Age_x'].astype(int)
grouped['Item ID'] = grouped['Item ID_x'].astype(int)

cols = [
    'Purchase_Count', 'SN', 'Age_x', 'Gender', 'Item ID_x', 'Item Name', 'Price',
    'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average_Purchase_Price', 'Purchase ID_y',
    'Age', 'Item ID', 'Total_Purchase_Value'
]

result = grouped[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_84/target_multisource_mcts.csv", index=False)