import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_31/training_1.csv", index_col=0)

agg_df1 = df1.groupby("State", as_index=False).agg({
    "English": "mean",
    "Math": "mean",
    "Reading": "mean",
    "Science": "mean",
    "Composite": "mean",
    "Participation": "first"
})

merged = pd.merge(df0, agg_df1, on="State", how="inner", suffixes=("_x", "_y"))

merged = merged.rename(columns={
    "Participation_x": "Participation_x",
    "Math_x": "Math_x",
    "Participation_y": "Participation_y",
    "Math_y": "Math_y"
})

result = merged[[
    "State",
    "Participation_x",
    "Evidence-Based Reading and Writing",
    "Math_x",
    "Total",
    "Participation_y",
    "English",
    "Math_y",
    "Reading",
    "Science",
    "Composite"
]]

result["Evidence-Based Reading and Writing"] = result["Evidence-Based Reading and Writing"].astype(int)
result["Math_x"] = result["Math_x"].astype(int)
result["Total"] = result["Total"].astype(int)
result["English"] = result["English"].astype(float)
result["Math_y"] = result["Math_y"].astype(float)
result["Reading"] = result["Reading"].astype(float)
result["Science"] = result["Science"].astype(float)
result["Composite"] = result["Composite"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_31/target_multisource_mcts.csv", index=False)