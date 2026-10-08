import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

merged = pd.merge(
    df0,
    df1,
    on="State",
    how="inner",
    suffixes=("_x", "_y")
)

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

merged["English"] = merged["English"].astype(float)
merged["Math_x"] = merged["Math_x"].astype(float)
merged["Reading"] = merged["Reading"].astype(float)
merged["Science"] = merged["Science"].astype(float)
merged["Composite"] = merged["Composite"].astype(float)
merged["Evidence-Based Reading and Writing"] = pd.to_numeric(merged["Evidence-Based Reading and Writing"], errors='coerce').astype('Int64')
merged["Math_y"] = pd.to_numeric(merged["Math_y"], errors='coerce').astype('Int64')
merged["Total"] = pd.to_numeric(merged["Total"], errors='coerce').astype('Int64')

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)