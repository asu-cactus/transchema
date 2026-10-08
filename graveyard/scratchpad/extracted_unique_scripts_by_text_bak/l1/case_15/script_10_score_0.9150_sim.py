import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

agg = df0.groupby("State").agg({
    "English": "max",
    "Math": "max",
    "Reading": "max",
    "Science": "max",
    "Composite": "max",
    "Participation": "max"
}).reset_index()

agg = agg.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

merged = pd.merge(agg, df1, on="State", how="inner", suffixes=("", "_y"))

merged = merged.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

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

merged["Evidence-Based Reading and Writing"] = merged["Evidence-Based Reading and Writing"].astype("Int64")
merged["Math_y"] = merged["Math_y"].astype("Int64")
merged["Total"] = merged["Total"].astype("Int64")

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)