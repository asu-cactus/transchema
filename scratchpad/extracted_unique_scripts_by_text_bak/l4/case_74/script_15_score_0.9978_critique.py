import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by Gender and count non-null values in other columns
result = df0.groupby('Gender').agg({
    'Purchase ID': 'count',
    'SN': 'count',
    'Age': 'count',
    'Item ID': 'count',
    'Item Name': 'count',
    'Price': 'count'
}).reset_index()

# Ensure column order matches target schema
result = result[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Convert all count columns to integer type
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    result[col] = result[col].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)