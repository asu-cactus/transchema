import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

agg0 = df0.groupby("State").agg({
    "English": "mean",
    "Math": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Participation": lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
}).reset_index()
agg0.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
}, inplace=True)

agg1 = df1.groupby("State").agg({
    "Evidence-Based Reading and Writing": "mean",
    "Math": "mean",
    "Total": "mean",
    "Participation": lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
}).reset_index()
agg1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
}, inplace=True)

merged = pd.merge(agg0, agg1, on="State", how="inner")

merged["Evidence-Based Reading and Writing"] = merged["Evidence-Based Reading and Writing"].round().astype("Int64")
merged["Math_y"] = merged["Math_y"].round().astype("Int64")
merged["Total"] = merged["Total"].round().astype("Int64")

merged = merged[[
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

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)