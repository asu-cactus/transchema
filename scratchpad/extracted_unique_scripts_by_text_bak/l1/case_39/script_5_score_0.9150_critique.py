import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Rename columns to match target schema exactly
df0 = df0.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

df1 = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

# Join on State with inner join
df = pd.merge(df0, df1, on="State", how="inner")

# Select columns in target schema order
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

# Convert integer columns to Int64 dtype
df["Evidence-Based Reading and Writing"] = df["Evidence-Based Reading and Writing"].astype("Int64")
df["Math_y"] = df["Math_y"].astype("Int64")
df["Total"] = df["Total"].astype("Int64")

# Save without index to avoid extra column
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)