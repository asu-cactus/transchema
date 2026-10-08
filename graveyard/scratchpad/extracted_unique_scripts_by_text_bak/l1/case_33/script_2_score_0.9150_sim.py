import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="State", suffixes=("_x", "_y"))

df = df.rename(columns={
    "Participation_x": "Participation_x",
    "Participation_y": "Participation_y",
    "Math_x": "Math_x",
    "Math_y": "Math_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "English": "English",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite",
    "Total": "Total",
    "State": "State"
})

df = df[[
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

df["Evidence-Based Reading and Writing"] = df["Evidence-Based Reading and Writing"].astype("Int64")
df["Math_y"] = df["Math_y"].astype("Int64")
df["Total"] = df["Total"].astype("Int64")

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv")