import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

agg = df0.groupby("Item ID").agg(
    Purchase_Count = ("Purchase ID", "count"),
    Item_Price = ("Price", "mean"),
    Total_Purchase_Value = ("Price", "sum")
).reset_index(drop=True)

agg["Purchase_Count"] = agg["Purchase_Count"].astype(int)
agg["Item_Price"] = agg["Item_Price"].round().astype(int)
agg["Total_Purchase_Value"] = agg["Total_Purchase_Value"].astype(float)

agg.rename(columns={
    "Purchase_Count": "Purchase Count",
    "Item_Price": "Item Price",
    "Total_Purchase_Value": "Total Purchase Value"
}, inplace=True)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)