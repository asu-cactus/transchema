import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Rename columns in df0 to match target suffixes
df0 = df0.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

# Rename columns in df1 to match target suffixes
df1 = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

# Join on State with inner join to keep only states present in both sources
merged = pd.merge(df0, df1, on="State", how="inner")

# Reorder columns to match target schema exactly
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

# Convert integer columns to Int64 dtype to match target schema
merged["Evidence-Based Reading and Writing"] = merged["Evidence-Based Reading and Writing"].astype("Int64")
merged["Math_y"] = merged["Math_y"].astype("Int64")
merged["Total"] = merged["Total"].astype("Int64")

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)