import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

grouped = df0.groupby('Gender', as_index=False).agg(
    Purchase_ID=('Purchase ID', 'nunique'),
    SN=('SN', 'nunique'),
    Age=('Age', 'nunique'),
    Item_ID=('Item ID', 'nunique'),
    Item_Name=('Item Name', 'nunique'),
    Price=('Price', 'sum')
)

# Rename columns to match target schema exactly
grouped.rename(columns={
    'Purchase_ID': 'Purchase ID',
    'Item_ID': 'Item ID',
    'Item_Name': 'Item Name'
}, inplace=True)

# Convert all columns except Gender to int as per target schema
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)