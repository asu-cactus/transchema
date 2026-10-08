import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

df0['Age Category'] = df0['Age'].astype(int)

df = df0.copy()

df['Purchase ID'] = df['Purchase ID'].astype(int)

df['SN'] = pd.to_numeric(df['SN'], errors='coerce')
df['SN'] = df['SN'].fillna(0).astype(int)

df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 2}).fillna(0).astype(int)

df['Item ID'] = pd.to_numeric(df['Item ID'], errors='coerce').fillna(0).astype(int)

df['Item Name'] = df['Item Name'].astype('category').cat.codes.astype(int)

df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0).astype(int)

grouped = df.groupby(['Age Category', 'Purchase ID', 'SN', 'Gender', 'Item ID', 'Item Name', 'Price'], as_index=False).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum')
)

grouped['Average Purchase Price'] = grouped['Total_Purchase_Value'] / grouped['Purchase_Count']

grouped.rename(columns={
    'Age Category': 'Age Category',
    'Purchase ID': 'Purchase ID',
    'SN': 'SN',
    'Purchase_Count': 'Purchase Count',
    'Gender': 'Gender',
    'Item ID': 'Item ID',
    'Item Name': 'Item Name',
    'Price': 'Price',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average Purchase Price': 'Average Purchase Price'
}, inplace=True)

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