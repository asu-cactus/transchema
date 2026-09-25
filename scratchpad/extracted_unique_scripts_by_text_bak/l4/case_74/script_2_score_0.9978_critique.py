import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by Gender and count Purchase ID for all columns except Gender
grouped = df0.groupby("Gender").agg({
    "Purchase ID": "count",
    "SN": "count",
    "Age": "count",
    "Item ID": "count",
    "Item Name": "count",
    "Price": "count"
}).reset_index()

# Rename columns to match target schema
grouped.columns = ['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']

# Convert all count columns to int
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)