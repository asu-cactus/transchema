import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema suffixes
df0_renamed = df0.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

# Rename columns in df1 to match target schema suffixes
df1_renamed = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

# Inner join on State
merged = pd.merge(df0_renamed, df1_renamed, on="State", how="inner")

# Select columns in target schema order
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

# Cast types to match target schema
result["English"] = result["English"].astype(float)
result["Math_x"] = result["Math_x"].astype(float)
result["Reading"] = result["Reading"].astype(float)
result["Science"] = result["Science"].astype(float)
result["Composite"] = result["Composite"].astype(float)
result["Evidence-Based Reading and Writing"] = pd.to_numeric(result["Evidence-Based Reading and Writing"], errors='coerce').astype('Int64')
result["Math_y"] = pd.to_numeric(result["Math_y"], errors='coerce').astype('Int64')
result["Total"] = pd.to_numeric(result["Total"], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)