import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_33/training_1.csv", index_col=0)

# Rename columns to match target schema
df0 = df0.rename(columns={"Participation": "Participation_x", "Math": "Math_x"})
df1 = df1.rename(columns={"Participation": "Participation_y", "Math": "Math_y"})

# Inner join on State
merged = pd.merge(df0, df1, on="State", how="inner")

# Reorder columns to match target schema exactly
cols_order = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
              'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[cols_order]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_33/target_multisource_mcts.csv", index=False)