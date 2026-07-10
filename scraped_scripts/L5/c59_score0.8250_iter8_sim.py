import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="Item ID")

grouped = df_joined.groupby("Item ID").agg(
    Purchase_Count=("Purchase ID_x", "count"),
    Item_Price=("Price_x", "first"),
)

grouped = grouped.reset_index()

grouped["Total Purchase Value"] = grouped["Purchase_Count"] * grouped["Item_Price"]

result = grouped.rename(columns={
    "Purchase_Count": "Purchase Count",
    "Item_Price": "Item Price"
})[["Purchase Count", "Item Price", "Total Purchase Value"]]

result["Purchase Count"] = result["Purchase Count"].astype(int)
result["Item Price"] = result["Item Price"].astype(int)
result["Total Purchase Value"] = result["Total Purchase Value"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)