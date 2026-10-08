import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

agg1 = df0.groupby('Age').agg(
    Purchase_ID_count=('Purchase ID', 'count'),
    SN_count_distinct=('SN', 'nunique'),
    Purchase_Count=('Purchase ID', 'count')
).reset_index()

agg2 = df0.groupby(['Age', 'Gender', 'Item ID', 'Item Name', 'Price']).agg(
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean')
).reset_index()

merged = pd.merge(agg2, agg1, on='Age', how='inner')

result = merged.rename(columns={
    'Age': 'Age Category',
    'Purchase_ID_count': 'Purchase ID',
    'SN_count_distinct': 'SN',
    'Purchase_Count': 'Purchase Count',
    'Gender': 'Gender',
    'Item ID': 'Item ID',
    'Item Name': 'Item Name',
    'Price': 'Price',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

result = result[['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)