import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

# Rename columns in df0 and df1 to avoid automatic suffixes during merge
df0_renamed = df0.rename(columns={
    "Participation": "Participation_x",
    "Math": "Math_x"
})

df1_renamed = df1.rename(columns={
    "Participation": "Participation_y",
    "Math": "Math_y"
})

# Inner join on 'State'
df_merged = pd.merge(df0_renamed, df1_renamed, on="State", how="inner")

# Convert integer columns to Int64 dtype (nullable integer)
df_merged["Evidence-Based Reading and Writing"] = df_merged["Evidence-Based Reading and Writing"].astype("Int64")
df_merged["Math_y"] = df_merged["Math_y"].astype("Int64")
df_merged["Total"] = df_merged["Total"].astype("Int64")

# Select columns in the exact order as target schema
df_merged = df_merged[[
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

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)