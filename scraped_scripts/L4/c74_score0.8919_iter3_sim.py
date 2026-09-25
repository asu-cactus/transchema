import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

df_joined = pd.merge(df0, df0, on="SN", suffixes=("", "_y"))

df_grouped = df_joined.groupby("Gender", as_index=False).agg({
    "Purchase ID": "sum",
    "SN": lambda x: pd.to_numeric(x, errors='coerce').sum(),
    "Age": "sum",
    "Item ID": "sum",
    "Item Name": lambda x: pd.to_numeric(x, errors='coerce').sum(),
    "Price": "sum"
})

df_grouped["Purchase ID"] = df_grouped["Purchase ID"].astype(int)
df_grouped["SN"] = df_grouped["SN"].fillna(0).astype(int)
df_grouped["Age"] = df_grouped["Age"].astype(int)
df_grouped["Item ID"] = df_grouped["Item ID"].astype(int)
df_grouped["Item Name"] = df_grouped["Item Name"].fillna(0).astype(int)
df_grouped["Price"] = df_grouped["Price"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)