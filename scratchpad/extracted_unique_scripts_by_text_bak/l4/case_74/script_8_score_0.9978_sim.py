import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

agg = df0.groupby("Gender").agg({
    "Purchase ID": "count",
    "SN": "count",
    "Age": "count",
    "Item ID": "count",
    "Item Name": "count",
    "Price": "count"
}).reset_index()

agg = agg.rename(columns={
    "Purchase ID": "Purchase ID",
    "SN": "SN",
    "Age": "Age",
    "Item ID": "Item ID",
    "Item Name": "Item Name",
    "Price": "Price"
})

agg["Purchase ID"] = agg["Purchase ID"].astype(int)
agg["SN"] = agg["SN"].astype(int)
agg["Age"] = agg["Age"].astype(int)
agg["Item ID"] = agg["Item ID"].astype(int)
agg["Item Name"] = agg["Item Name"].astype(int)
agg["Price"] = agg["Price"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)