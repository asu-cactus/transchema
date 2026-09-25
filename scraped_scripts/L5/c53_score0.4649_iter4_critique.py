import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

bins = [0, 17, 24, 34, 44, 54, 64, 150]
labels = [1, 2, 3, 4, 5, 6, 7]
df0['Age Category'] = pd.cut(df0['Age'], bins=bins, labels=labels, right=True).astype(int)

df0['Purchase Count'] = 1
df0['Total Purchase Value'] = df0['Price'] * df0['Purchase Count']
df0['Average Purchase Price'] = df0['Price']

gender_map = {'Male': 1, 'Female': 2}
df0['Gender'] = df0['Gender'].map(gender_map).fillna(0).astype(int)

df0['Item Name'] = df0['Item Name'].astype('category').cat.codes + 1
df0['SN'] = df0['SN'].astype('category').cat.codes + 1

group_cols = ['Age Category', 'Purchase ID', 'SN', 'Gender', 'Item ID', 'Item Name']

agg_df = df0.groupby(group_cols).agg({
    'Purchase Count': 'sum',
    'Price': 'mean',
    'Total Purchase Value': 'sum',
    'Average Purchase Price': 'mean'
}).reset_index()

# Convert 'Price' to int as in target schema
agg_df['Price'] = agg_df['Price'].round().astype(int)

# Ensure columns order matches target schema
target_cols = ['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']
agg_df = agg_df[target_cols]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)