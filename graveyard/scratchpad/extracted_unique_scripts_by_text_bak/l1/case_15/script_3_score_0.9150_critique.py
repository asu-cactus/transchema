import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema (remove suffixes, use exact target column names)
# Target columns from df0: Participation_x, Math_x
df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

# Rename columns in df1 to match target schema (Participation_y, Math_y)
df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Join on 'State' with inner join to keep only states present in both sources (matches target row count)
merged = pd.merge(df0, df1, on='State', how='inner')

# Select columns exactly as in target schema
final_cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
              'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[final_cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)