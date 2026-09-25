import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_1.csv", index_col=0)

# Inner join on 'State'
df = pd.merge(df0, df1, on="State", how="inner", suffixes=("_x", "_y"))

# Rename columns to match target schema exactly
df = df.rename(columns={
    "Participation_x": "Participation_x",
    "Participation_y": "Participation_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math_x": "Math_x",
    "Total": "Total",
    "English": "English",
    "Math_y": "Math_y",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite"
})

# Select columns in target schema order
df = df[[
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
df["Participation_x"] = df["Participation_x"].astype(str)
df["Participation_y"] = df["Participation_y"].astype(str)

df["Evidence-Based Reading and Writing"] = pd.to_numeric(df["Evidence-Based Reading and Writing"], errors='coerce').astype('Int64')
df["Math_x"] = pd.to_numeric(df["Math_x"], errors='coerce').astype('Int64')
df["Total"] = pd.to_numeric(df["Total"], errors='coerce').astype('Int64')

df["English"] = pd.to_numeric(df["English"], errors='coerce')
df["Math_y"] = pd.to_numeric(df["Math_y"], errors='coerce')
df["Reading"] = pd.to_numeric(df["Reading"], errors='coerce')
df["Science"] = pd.to_numeric(df["Science"], errors='coerce')
df["Composite"] = pd.to_numeric(df["Composite"], errors='coerce')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts.csv", index=False)