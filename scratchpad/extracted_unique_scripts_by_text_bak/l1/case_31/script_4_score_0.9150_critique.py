import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_31/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_31/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="State", suffixes=("_x", "_y"), how='inner')

# Drop rows with any NaN values to ensure only matching states remain
df = df.dropna()

# Select and reorder columns exactly as in target schema
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

# Convert columns to correct types
df["Evidence-Based Reading and Writing"] = pd.to_numeric(df["Evidence-Based Reading and Writing"], errors='coerce').astype('Int64')
df["Math_x"] = pd.to_numeric(df["Math_x"], errors='coerce').astype('Int64')
df["Total"] = pd.to_numeric(df["Total"], errors='coerce').astype('Int64')

df["English"] = pd.to_numeric(df["English"], errors='coerce')
df["Math_y"] = pd.to_numeric(df["Math_y"], errors='coerce')
df["Reading"] = pd.to_numeric(df["Reading"], errors='coerce')
df["Science"] = pd.to_numeric(df["Science"], errors='coerce')
df["Composite"] = pd.to_numeric(df["Composite"], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_31/target_multisource_mcts.csv", index=False)