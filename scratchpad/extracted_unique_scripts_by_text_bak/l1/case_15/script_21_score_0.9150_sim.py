import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

agg = df1.groupby("State").agg({
    "Evidence-Based Reading and Writing": "sum",
    "Math": "sum",
    "Total": "sum",
    "Participation": "first"
}).reset_index()

df0 = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})
agg = agg.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

merged = pd.merge(df0, agg, on="State", how="inner")

result = merged[[
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)