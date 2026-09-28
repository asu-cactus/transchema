import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_45/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="State", how="inner", suffixes=("_x", "_y"))

# Rename columns to match target schema exactly
merged = merged.rename(columns={
    "Participation_x": "Participation_x",
    "English": "English",
    "Math_x": "Math_x",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite",
    "Participation_y": "Participation_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math_y": "Math_y",
    "Total": "Total"
})

# Select columns in the exact order of target schema
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

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_45/target_multisource_mcts.csv", index=False)