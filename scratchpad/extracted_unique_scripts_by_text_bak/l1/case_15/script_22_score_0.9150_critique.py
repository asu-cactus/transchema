import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema (no suffixes)
df0 = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})

# Rename columns in df1 to match target schema (no suffixes)
df1 = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

# Join on 'State' with inner join
merged = pd.merge(df0, df1, on="State", how="inner")

# Select columns in the exact order of the target schema
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

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)