import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Join on 'State' with inner join (default)
merged = pd.merge(df0, df1, on="State", suffixes=("_x", "_y"))

# Rename columns to match target schema exactly (remove suffixes)
merged = merged.rename(columns={
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
})

# Select columns in the exact order of target schema
final_cols = [
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
]

result = merged[final_cols]

# Ensure Participation columns are strings (as in target)
result["Participation_x"] = result["Participation_x"].astype(str)
result["Participation_y"] = result["Participation_y"].astype(str)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)