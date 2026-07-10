import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

grouped = df0.groupby("Price").agg(
    Purchase_Count=("Purchase ID", "count"),
    Item_Price=("Price", "mean")
).reset_index()

grouped["Purchase Count"] = grouped["Purchase_Count"].astype(int)
grouped["Item Price"] = grouped["Item_Price"].round().astype(int)
grouped["Total Purchase Value"] = grouped["Purchase Count"] * grouped["Item Price"] * 1.0

result = grouped[["Purchase Count", "Item Price", "Total Purchase Value"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)