import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Join on 'State' column
merged = pd.merge(df0, df1, on='State', how='inner', suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
merged.rename(columns={
    'Participation_x': 'Participation_x',
    'Participation_y': 'Participation_y',
    'Math_x': 'Math_x',
    'Math_y': 'Math_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Total': 'Total',
    'English': 'English',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite'
}, inplace=True)

# Select columns in the exact order of target schema
merged = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Write output
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)