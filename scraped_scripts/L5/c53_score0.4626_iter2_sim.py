import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

agg = df0.groupby("Gender").agg(
    Purchase_ID_Count = ("Purchase ID", "count"),
    SN_Count = ("SN", "count"),
    Item_ID_Count = ("Item ID", "count"),
    Item_Name_Count = ("Item Name", "count"),
    Price_Count = ("Price", "count"),
    Age_Category = ("Age", "mean"),
    Average_Purchase_Price = ("Price", "mean"),
    Total_Purchase_Value = ("Price", "sum"),
).reset_index()

agg["Age Category"] = agg["Age_Category"].round().astype(int)
agg["Purchase ID"] = agg["Purchase_ID_Count"].astype(int)
agg["SN"] = agg["SN_Count"].astype(int)
agg["Purchase Count"] = agg["Item_ID_Count"].astype(int)
agg["Gender"] = agg["Gender"].astype('category').cat.codes.astype(int)
agg["Item ID"] = agg["Item_ID_Count"].astype(int)
agg["Item Name"] = agg["Item_Name_Count"].astype(int)
agg["Price"] = agg["Price_Count"].astype(int)
agg["Total Purchase Value"] = agg["Total_Purchase_Value"].astype(float)
agg["Average Purchase Price"] = agg["Average_Purchase_Price"].astype(float)

result = agg[[
    "Age Category",
    "Purchase ID",
    "SN",
    "Purchase Count",
    "Gender",
    "Item ID",
    "Item Name",
    "Price",
    "Total Purchase Value",
    "Average Purchase Price"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)