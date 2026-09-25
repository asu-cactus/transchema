import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df_grouped = df0.groupby("Gender", as_index=False).agg({
    "Purchase ID": "count",
    "SN": "count",
    "Age": "count",
    "Item ID": "count",
    "Item Name": "count",
    "Price": "count"
})

df_grouped = df_grouped.rename(columns={
    "Purchase ID": "Purchase ID",
    "SN": "SN",
    "Age": "Age",
    "Item ID": "Item ID",
    "Item Name": "Item Name",
    "Price": "Price"
})

df_grouped["Purchase ID"] = df_grouped["Purchase ID"].astype(int)
df_grouped["SN"] = df_grouped["SN"].astype(int)
df_grouped["Age"] = df_grouped["Age"].astype(int)
df_grouped["Item ID"] = df_grouped["Item ID"].astype(int)
df_grouped["Item Name"] = df_grouped["Item Name"].astype(int)
df_grouped["Price"] = df_grouped["Price"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)