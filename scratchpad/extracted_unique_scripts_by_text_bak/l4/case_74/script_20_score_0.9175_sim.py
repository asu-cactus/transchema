import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="Purchase ID", suffixes=("", "_dup"))

grouped = df_joined.groupby("Gender").agg({
    "Purchase ID": "first",
    "SN": "first",
    "Age": "first",
    "Item ID": "first",
    "Item Name": "first",
    "Price": "first"
}).reset_index()

grouped["Purchase ID"] = grouped["Purchase ID"].astype(int)
grouped["SN"] = pd.to_numeric(grouped["SN"], errors='coerce').fillna(0).astype(int)
grouped["Age"] = grouped["Age"].astype(int)
grouped["Item ID"] = grouped["Item ID"].astype(int)
grouped["Item Name"] = pd.to_numeric(grouped["Item Name"], errors='coerce').fillna(0).astype(int)
grouped["Price"] = grouped["Price"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)