import pandas as pd

# Read source CSVs with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_31/training_1.csv", index_col=0)

# Perform inner join on 'State'
merged = pd.merge(df0, df1, on="State", how="inner", suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
merged = merged.rename(columns={
    "Participation_x": "Participation_x",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math_x": "Math_x",
    "Total": "Total",
    "Participation_y": "Participation_y",
    "English": "English",
    "Math_y": "Math_y",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite"
})

# Select columns in target schema order
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

# Convert data types to match target schema
result["Evidence-Based Reading and Writing"] = result["Evidence-Based Reading and Writing"].astype(int)
result["Math_x"] = result["Math_x"].astype(int)
result["Total"] = result["Total"].astype(int)

result["English"] = result["English"].astype(float)
result["Math_y"] = result["Math_y"].astype(float)
result["Reading"] = result["Reading"].astype(float)
result["Science"] = result["Science"].astype(float)
result["Composite"] = result["Composite"].astype(float)

# Write output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_31/target_multisource_mcts.csv", index=False)