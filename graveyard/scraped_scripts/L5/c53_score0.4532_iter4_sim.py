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

target_cols = ['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']
df_target = df0[target_cols]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)