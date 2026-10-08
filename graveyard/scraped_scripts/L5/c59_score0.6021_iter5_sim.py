import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

agg = df0.groupby("Purchase ID").agg(
    Purchase_Count=("Item ID", "count"),
    Total_Purchase_Value=("Price", "sum")
).reset_index()

agg["Item Price"] = agg["Purchase_Count"]

agg = agg.rename(columns={
    "Purchase_Count": "Purchase Count",
    "Total_Purchase_Value": "Total Purchase Value"
})

agg["Purchase Count"] = agg["Purchase Count"].astype(int)
agg["Item Price"] = agg["Item Price"].astype(int)
agg["Total Purchase Value"] = agg["Total Purchase Value"].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)