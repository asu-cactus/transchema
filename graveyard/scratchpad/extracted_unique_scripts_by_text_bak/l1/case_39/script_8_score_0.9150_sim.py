import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

agg_0 = df0.groupby("State", as_index=False).agg({
    "English": "mean",
    "Math": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Participation": "first"
}).rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

df1_renamed = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

result = pd.merge(agg_0, df1_renamed, on="State", how="inner")

result = result[[
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

result["Evidence-Based Reading and Writing"] = result["Evidence-Based Reading and Writing"].astype("Int64")
result["Math_y"] = result["Math_y"].astype("Int64")
result["Total"] = result["Total"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)