import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

df_joined = df.merge(df, on="Purchase ID", suffixes=('_x', '_y'))

agg = df_joined.groupby("Gender").agg(
    Purchase_Count=("Purchase ID", "count"),
    SN=("SN_x", lambda x: x.nunique()),
    Age_x=("Age_x", "mean"),
    Item_ID_x=("Item ID_x", "mean"),
    Item_Name=("Item Name_x", lambda x: x.nunique()),
    Price=("Price_x", "mean"),
    Purchase_ID_x=("Purchase ID_x", "mean"),
    Age_y=("Age_y", "mean"),
    Item_ID_y=("Item ID_y", "mean"),
    Average_Purchase_Price=("Price_y", "mean"),
    Purchase_ID_y=("Purchase ID_y", "count"),
    Age=("Age_y", "sum"),
    Item_ID=("Item ID_y", "sum"),
    Total_Purchase_Value=("Price_y", "sum"),
).reset_index()

agg["Purchase Count"] = agg["Purchase_Count"].astype(int)
agg["SN"] = agg["SN"].astype(int)
agg["Age_x"] = agg["Age_x"].round().astype(int)
agg["Item ID_x"] = agg["Item_ID_x"].round().astype(int)
agg["Item Name"] = agg["Item_Name"].astype(int)
agg["Price"] = agg["Price"].round().astype(int)
agg["Purchase ID_x"] = agg["Purchase_ID_x"].astype(float)
agg["Age_y"] = agg["Age_y"].astype(float)
agg["Item ID_y"] = agg["Item_ID_y"].astype(float)
agg["Average Purchase Price"] = agg["Average_Purchase_Price"].astype(float)
agg["Purchase ID_y"] = agg["Purchase_ID_y"].astype(int)
agg["Age"] = agg["Age"].astype(int)
agg["Item ID"] = agg["Item_ID"].astype(int)
agg["Total Purchase Value"] = agg["Total_Purchase_Value"].astype(float)

result = agg[[
    "Gender", "Purchase Count", "SN", "Age_x", "Item ID_x", "Item Name", "Price",
    "Purchase ID_x", "Age_y", "Item ID_y", "Average Purchase Price", "Purchase ID_y",
    "Age", "Item ID", "Total Purchase Value"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)