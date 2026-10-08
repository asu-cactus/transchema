import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

df0["Item Price"] = df0["Price"].astype(int)

grouped = df0.groupby("Item Price").agg(
    Purchase_Count=("Purchase ID", "count"),
    Total_Purchase_Value=("Price", "sum")
).reset_index()

grouped["Purchase Count"] = grouped["Purchase_Count"].astype(int)
grouped["Item Price"] = grouped["Item Price"].astype(int)
grouped["Total Purchase Value"] = grouped["Total_Purchase_Value"].astype(float)

result = grouped[["Purchase Count", "Item Price", "Total Purchase Value"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)