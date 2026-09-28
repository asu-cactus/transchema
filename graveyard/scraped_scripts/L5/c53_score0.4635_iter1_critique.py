import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

def age_category(age):
    return int(age // 5 * 5 + 3)

df = df0.copy()

df['Age Category'] = df['Age'].apply(age_category)
df['Purchase Count'] = 1
df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 2}).fillna(0).astype(int)
df['Item Name'] = df['Item Name'].astype('category').cat.codes + 1
df['SN'] = df['SN'].astype('category').cat.codes + 1

df['Total Purchase Value'] = df['Price'] * df['Purchase Count']
df['Average Purchase Price'] = df['Price']

group_cols = ['Age Category', 'Purchase ID', 'SN', 'Gender', 'Item ID', 'Item Name', 'Price']

agg_df = df.groupby(group_cols).agg({
    'Purchase Count': 'sum',
    'Total Purchase Value': 'sum',
    'Average Purchase Price': 'mean'
}).reset_index()

# Reorder columns to match target schema
agg_df = agg_df[['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)