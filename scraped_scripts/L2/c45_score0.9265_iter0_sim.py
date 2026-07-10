import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_45/training_0.csv", index_col=0)

grouped = df0.groupby("Item ID", as_index=False).agg({
    "Item Name": "first",
    "Price": "first"
})

grouped["Item ID"] = grouped["Item ID"].astype(int)
grouped["Item Name"] = grouped["Item Name"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_45/target_multisource_mcts.csv", index=False)