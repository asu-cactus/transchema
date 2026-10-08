import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

# Rename Participation columns to match target schema
df0 = df0.rename(columns={"Participation": "Participation_x"})
df1 = df1.rename(columns={"Participation": "Participation_y"})

# Merge on State (inner join)
df_merged = pd.merge(df0, df1, how="inner", on="State")

# Rename columns to match target schema exactly
# The target schema has:
# ['State': string, 'Participation_x': string, 'English': float, 'Math_x': float, 'Reading': float, 'Science': float, 'Composite': float,
#  'Participation_y': string, 'Evidence-Based Reading and Writing': integer, 'Math_y': integer, 'Total': integer]

# Rename Math columns to Math_x and Math_y accordingly
df_merged = df_merged.rename(columns={
    "Math_x": "Math_x",  # from df0, already named Math in df0, rename to Math_x
    "Math_y": "Math_y"   # from df1, already named Math in df1, rename to Math_y
})

# Actually, after merge, columns are:
# State, Participation_x, English, Math, Reading, Science, Composite, Participation_y, Evidence-Based Reading and Writing, Math, Total
# So we need to rename the two Math columns to Math_x and Math_y:
# The Math from df0 is "Math" before merge, after merge it becomes "Math_x" automatically if suffixes are used.
# But since we did not specify suffixes, both "Math" columns will collide and pandas will add suffixes automatically.
# To avoid confusion, let's specify suffixes in merge.

df_merged = pd.merge(df0, df1, how="inner", on="State", suffixes=('_x', '_y'))

# Now columns are:
# State, Participation_x, English, Math_x, Reading, Science, Composite, Participation_y, Evidence-Based Reading and Writing, Math_y, Total

# Convert columns to correct types
df_merged["English"] = df_merged["English"].astype(float)
df_merged["Math_x"] = df_merged["Math_x"].astype(float)
df_merged["Reading"] = df_merged["Reading"].astype(float)
df_merged["Science"] = df_merged["Science"].astype(float)
df_merged["Composite"] = df_merged["Composite"].astype(float)
df_merged["Evidence-Based Reading and Writing"] = df_merged["Evidence-Based Reading and Writing"].astype("Int64")
df_merged["Math_y"] = df_merged["Math_y"].astype("Int64")
df_merged["Total"] = df_merged["Total"].astype("Int64")

# Select columns in target schema order
df_merged = df_merged[[
    "State", "Participation_x", "English", "Math_x", "Reading", "Science", "Composite",
    "Participation_y", "Evidence-Based Reading and Writing", "Math_y", "Total"
]]

# Write output
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)