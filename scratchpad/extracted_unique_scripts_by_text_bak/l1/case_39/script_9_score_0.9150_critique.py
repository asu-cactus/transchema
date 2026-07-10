import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Rename columns in df1 to match target schema (no suffixes)
df1_renamed = df1.rename(columns={
    "Participation": "Participation_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "Math": "Math_y",
    "Total": "Total"
})

# Join on State with inner join
result = pd.merge(df0, df1_renamed, on="State", how="inner")

# Rename Participation in df0 to Participation_x to match target schema
result = result.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

# Reorder columns to match target schema exactly
result = result[[
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
result["Evidence-Based Reading and Writing"] = result["Evidence-Based Reading and Writing"].astype("Int64")
result["Math_y"] = result["Math_y"].astype("Int64")
result["Total"] = result["Total"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)