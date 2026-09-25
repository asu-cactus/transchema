import pandas as pd

# Read source CSVs with index_col=0 to ignore the first index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Perform inner join on 'State'
df_merged = pd.merge(df0, df1, on="State", how="inner", suffixes=("_x", "_y"))

# Rename columns to match target schema exactly (no suffixes except for Math and Participation columns)
df_merged.rename(columns={
    "Participation_x": "Participation_x",
    "Participation_y": "Participation_y",
    "Math_x": "Math_x",
    "Math_y": "Math_y",
    "Evidence-Based Reading and Writing": "Evidence-Based Reading and Writing",
    "English": "English",
    "Reading": "Reading",
    "Science": "Science",
    "Composite": "Composite",
    "Total": "Total"
}, inplace=True)

# Group by 'State' to remove duplicates if any, no aggregation needed, so just take first occurrence
df_final = df_merged.groupby("State", as_index=False).first()

# Reorder columns to match target schema exactly
df_final = df_final[[
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

# Write to target CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)