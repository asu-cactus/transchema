import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

df = df0.copy()

def age_category(age):
    return int(age // 5 * 5 + 3)

df['Age Category'] = df['Age'].apply(age_category)
df['Purchase Count'] = 1
df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 2}).fillna(0).astype(int)
df['Item Name'] = df['Item Name'].astype('category').cat.codes + 1
df['Total Purchase Value'] = df['Price'] * df['Purchase Count']
df['Average Purchase Price'] = df['Price']

df = df.rename(columns={
    'Age Category': 'Age Category',
    'Purchase ID': 'Purchase ID',
    'SN': 'SN',
    'Purchase Count': 'Purchase Count',
    'Gender': 'Gender',
    'Item ID': 'Item ID',
    'Item Name': 'Item Name',
    'Price': 'Price',
    'Total Purchase Value': 'Total Purchase Value',
    'Average Purchase Price': 'Average Purchase Price'
})

df = df[['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)