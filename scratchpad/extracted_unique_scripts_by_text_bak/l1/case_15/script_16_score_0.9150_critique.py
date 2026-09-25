import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Join on 'State' with suffixes to distinguish columns with same names
df = pd.merge(df0, df1, on="State", suffixes=("_x", "_y"))

# Rename columns to match target schema exactly (no suffixes except for Math and Participation columns)
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
})

# Select columns in the exact order of the target schema
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

# Convert integer columns to Int64 dtype to match target schema
df["Evidence-Based Reading and Writing"] = df["Evidence-Based Reading and Writing"].astype("Int64")
df["Math_y"] = df["Math_y"].astype("Int64")
df["Total"] = df["Total"].astype("Int64")

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv")