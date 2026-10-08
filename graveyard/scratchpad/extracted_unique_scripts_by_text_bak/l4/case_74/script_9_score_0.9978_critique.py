import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

agg = df0.groupby("Gender").agg({
    "Purchase ID": "count"
}).reset_index()

# Since target schema has all columns except Gender as the same integer count,
# replicate the count column to all required columns
agg["Purchase ID"] = agg["Purchase ID"].astype(int)
agg["SN"] = agg["Purchase ID"]
agg["Age"] = agg["Purchase ID"]
agg["Item ID"] = agg["Purchase ID"]
agg["Item Name"] = agg["Purchase ID"]
agg["Price"] = agg["Purchase ID"]

# Reorder columns to match target schema
agg = agg[["Gender", "Purchase ID", "SN", "Age", "Item ID", "Item Name", "Price"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)