import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

grouped = df0.groupby("Gender").agg(
    **{
        "Purchase Count": ("Purchase ID", "count"),
        "SN": ("SN", "count"),
        "Age_x": ("Age", "count"),
        "Item ID_x": ("Item ID", "count"),
        "Item Name": ("Item Name", "count"),
        "Price": ("Price", "count"),
        "Average Purchase Price": ("Price", "mean"),
        "Total Purchase Value": ("Price", "sum"),
    }
).reset_index()

# For columns in target schema not covered by above aggregations, create columns with NaN or appropriate types
grouped["Purchase ID_x"] = grouped["Average Purchase Price"] * 0  # float column with zeros
grouped["Age_y"] = grouped["Average Purchase Price"] * 0
grouped["Item ID_y"] = grouped["Average Purchase Price"] * 0
grouped["Purchase ID_y"] = grouped["Purchase Count"].astype(float) * 0
grouped["Age"] = grouped["Purchase Count"].astype(float) * 0
grouped["Item ID"] = grouped["Purchase Count"].astype(float) * 0
grouped["SN"] = grouped["SN"].astype(int)
grouped["Age_x"] = grouped["Age_x"].astype(int)
grouped["Item ID_x"] = grouped["Item ID_x"].astype(int)
grouped["Item Name"] = grouped["Item Name"].astype(int)
grouped["Price"] = grouped["Price"].astype(int)
grouped["Purchase ID_x"] = grouped["Purchase ID_x"].astype(float)
grouped["Age_y"] = grouped["Age_y"].astype(float)
grouped["Item ID_y"] = grouped["Item ID_y"].astype(float)
grouped["Average Purchase Price"] = grouped["Average Purchase Price"].astype(float)
grouped["Purchase ID_y"] = grouped["Purchase ID_y"].astype(int)
grouped["Age"] = grouped["Age"].astype(int)
grouped["Item ID"] = grouped["Item ID"].astype(int)
grouped["Total Purchase Value"] = grouped["Total Purchase Value"].astype(float)

grouped = grouped[
    [
        "Gender",
        "Purchase Count",
        "SN",
        "Age_x",
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
        "Total Purchase Value",
    ]
]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)