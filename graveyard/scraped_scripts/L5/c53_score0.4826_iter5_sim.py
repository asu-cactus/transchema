import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

grouped = df.groupby([
    "Purchase ID", "SN", "Age", "Gender", "Item ID", "Item Name", "Price"
], as_index=False).agg(
    Purchase_Count=("Purchase ID", "count"),
    Total_Purchase_Value=("Price", "sum"),
    Average_Purchase_Price=("Price", "mean")
)

grouped = grouped.rename(columns={
    "Age": "Age Category",
    "Purchase ID": "Purchase ID",
    "SN": "SN",
    "Gender": "Gender",
    "Item ID": "Item ID",
    "Item Name": "Item Name",
    "Price": "Price",
    "Purchase_Count": "Purchase Count",
    "Total_Purchase_Value": "Total Purchase Value",
    "Average_Purchase_Price": "Average Purchase Price"
})

grouped["Age Category"] = grouped["Age Category"].astype(int)
grouped["Purchase ID"] = grouped["Purchase ID"].astype(int)
grouped["SN"] = grouped["SN"].astype(str)
grouped["Purchase Count"] = grouped["Purchase Count"].astype(int)
grouped["Gender"] = grouped["Gender"].astype(str)
grouped["Item ID"] = grouped["Item ID"].astype(int)
grouped["Item Name"] = grouped["Item Name"].astype(str)
grouped["Price"] = grouped["Price"].astype(int)
grouped["Total Purchase Value"] = grouped["Total Purchase Value"].astype(float)
grouped["Average Purchase Price"] = grouped["Average Purchase Price"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)