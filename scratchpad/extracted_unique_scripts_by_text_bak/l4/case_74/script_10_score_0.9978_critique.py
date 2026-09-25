import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

grouped = df0.groupby("Gender").agg({
    "Purchase ID": "count",
    "SN": "count",
    "Age": "count",
    "Item ID": "count",
    "Item Name": "count",
    "Price": "count"
}).reset_index()

# Ensure correct types as per target schema
grouped["Purchase ID"] = grouped["Purchase ID"].astype(int)
grouped["SN"] = grouped["SN"].astype(int)
grouped["Age"] = grouped["Age"].astype(int)
grouped["Item ID"] = grouped["Item ID"].astype(int)
grouped["Item Name"] = grouped["Item Name"].astype(int)
grouped["Price"] = grouped["Price"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)