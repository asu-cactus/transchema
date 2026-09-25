import pandas as pd

# Read source tables with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Inner join on 'State' to keep only states present in both sources
df = pd.merge(df0, df1, on="State", how="inner", suffixes=("_x", "_y"))

# Rename columns to match target schema exactly
df = df.rename(columns={
    "Participation_x": "Participation_x",
    "Participation_y": "Participation_y",
    "English": "English",
    "Math_x": "Math_x",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math_y": "Math_y",
    "Total": "Total"
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

# Convert integer columns to integer dtype
df["Evidence-Based Reading and Writing"] = df["Evidence-Based Reading and Writing"].astype("Int64")
df["Math_y"] = df["Math_y"].astype("Int64")
df["Total"] = df["Total"].astype("Int64")

# Write output CSV without the index column
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)