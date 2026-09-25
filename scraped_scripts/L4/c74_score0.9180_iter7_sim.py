import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="Purchase ID", suffixes=("", "_y"))

df_grouped = df_joined.groupby("Gender", as_index=False).agg({
    "Purchase ID": "first",
    "SN": "first",
    "Age": "first",
    "Item ID": "first",
    "Item Name": "first",
    "Price": "first"
})

df_grouped["Purchase ID"] = pd.to_numeric(df_grouped["Purchase ID"], errors="coerce").fillna(0).astype(int)
df_grouped["SN"] = pd.to_numeric(df_grouped["SN"], errors="coerce").fillna(0).astype(int)
df_grouped["Age"] = pd.to_numeric(df_grouped["Age"], errors="coerce").fillna(0).astype(int)
df_grouped["Item ID"] = pd.to_numeric(df_grouped["Item ID"], errors="coerce").fillna(0).astype(int)
df_grouped["Item Name"] = pd.to_numeric(df_grouped["Item Name"], errors="coerce").fillna(0).astype(int)
df_grouped["Price"] = pd.to_numeric(df_grouped["Price"], errors="coerce").fillna(0).astype(int)

df_grouped = df_grouped[["Gender", "Purchase ID", "SN", "Age", "Item ID", "Item Name", "Price"]]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)