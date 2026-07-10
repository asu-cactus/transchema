import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

grouped = df0.groupby("Price").agg(
    Purchase_Count=("Purchase ID", "count"),
    Total_Purchase_Value=("Price", "sum")
).reset_index()

grouped["Purchase Count"] = grouped["Purchase_Count"].astype(int)
grouped["Item Price"] = grouped["Price"].astype(int)
grouped["Total Purchase Value"] = grouped["Total_Purchase_Value"].astype(float)

result = grouped[["Purchase Count", "Item Price", "Total Purchase Value"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)