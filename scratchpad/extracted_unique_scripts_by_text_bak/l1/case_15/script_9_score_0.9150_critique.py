import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Join on 'State' with inner join to keep only states present in both sources
merged = pd.merge(df0, df1, on="State", how="inner", suffixes=('_x', '_y'))

# Rename columns to match target schema exactly (remove suffixes)
merged.rename(columns={
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
}, inplace=True)

# Ensure correct column order as per target schema
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

# Convert numeric columns to correct types
merged["English"] = merged["English"].astype(float)
merged["Math_x"] = merged["Math_x"].astype(float)
merged["Reading"] = merged["Reading"].astype(float)
merged["Science"] = merged["Science"].astype(float)
merged["Composite"] = merged["Composite"].astype(float)

merged["Evidence-Based Reading and Writing"] = merged["Evidence-Based Reading and Writing"].astype("Int64")
merged["Math_y"] = merged["Math_y"].astype("Int64")
merged["Total"] = merged["Total"].astype("Int64")

# Write output
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)