import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

df0_grouped = df0.groupby("State", as_index=False).agg({
    "Participation": "first",
    "English": "mean",
    "Math": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean"
}).rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

df1_grouped = df1.groupby("State", as_index=False).agg({
    "Participation": "first",
    "Evidence-Based Reading and Writing": "mean",
    "Math": "mean",
    "Total": "mean"
}).rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Total": "Total"
})

df_merged = pd.merge(df0_grouped, df1_grouped, on="State", how="inner")

df_merged["Evidence-Based Reading and Writing"] = df_merged["Evidence-Based Reading and Writing"].astype("Int64")
df_merged["Math_y"] = df_merged["Math_y"].astype("Int64")
df_merged["Total"] = df_merged["Total"].astype("Int64")

df_merged = df_merged[[
    "State",
    "Participation_x",
    "English",
    "Math_x",
    "Reading",
    "Science",
    "Composite",
    "Participation_y",
    "Evidence-Based Reading and Writing",
    "Math_y",
    "Total"
]]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)