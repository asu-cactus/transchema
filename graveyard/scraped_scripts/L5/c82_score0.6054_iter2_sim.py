import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

grouped = df0.groupby(
    ['Item ID', 'Item Name', 'Purchase ID', 'SN', 'Age', 'Gender'],
    as_index=False
).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum')
)

grouped.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Total_Purchase_Value': 'Total Purchase Value'
}, inplace=True)

grouped['Purchase ID_x'] = grouped['Purchase ID']
grouped['Age_x'] = grouped['Age']
grouped['Gender'] = grouped['Gender'].astype('int', errors='ignore')  # Gender is integer in target, source is string, so convert if possible
# Convert Gender string to integer if possible, else map or leave as is
# Since source Gender is string (Male/Female), target expects integer, we map:
gender_map = {'Male': 1, 'Female': 2}
grouped['Gender'] = grouped['Gender'].map(gender_map).fillna(0).astype(int)

grouped['Purchase ID_y'] = grouped['Purchase ID'].astype(float)
grouped['Age_y'] = grouped['Age'].astype(float)
grouped['Item Price'] = grouped['Total Purchase Value'] / grouped['Purchase Count']
grouped['Purchase ID'] = grouped['Purchase ID']
grouped['Age'] = grouped['Age']

final_cols = [
    'Item ID', 'Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender',
    'Purchase Count', 'Purchase ID_y', 'Age_y', 'Item Price',
    'Purchase ID', 'Age', 'Total Purchase Value'
]

result = grouped[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)