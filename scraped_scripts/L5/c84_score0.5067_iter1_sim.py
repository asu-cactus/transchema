import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_84/training_0.csv", index_col=0)

df_joined = df0.merge(df0, on="SN", suffixes=("_x", "_y"))

df_joined["Purchase Count"] = 1
df_joined["Purchase Count"] = df_joined.groupby("SN")["Purchase Count"].transform("count")

df_joined["Purchase ID_x"] = df_joined["Purchase ID_x"].astype(float)
df_joined["Purchase ID_y"] = df_joined["Purchase ID_y"].astype(int)
df_joined["Item ID_y"] = df_joined["Item ID_y"].astype(float)
df_joined["Average Purchase Price"] = df_joined["Price_x"].astype(float)
df_joined["Total Purchase Value"] = (df_joined["Price_x"] * df_joined["Purchase Count"]).astype(float)

df_result = df_joined[[
    "Purchase Count",
    "SN",
    "Age_x",
    "Gender_x",
    "Item ID_x",
    "Item Name_x",
    "Price_x",
    "Purchase ID_x",
    "Age_y",
    "Item ID_y",
    "Average Purchase Price",
    "Purchase ID_y",
    "Age_x",
    "Item ID_x",
    "Total Purchase Value"
]]

df_result.columns = [
    "Purchase Count",
    "SN",
    "Age_x",
    "Gender",
    "Item ID_x",
    "Item Name",
    "Price",
    "Purchase ID_x",
    "Age_y",
    "Item ID_y",
    "Average Purchase Price",
    "Purchase ID_y",
    "Age",
    "Item ID",
    "Total Purchase Value"
]

df_result["Gender"] = df_result["Gender"].astype('category').cat.codes

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_84/target_multisource_mcts.csv", index=False)