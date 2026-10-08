import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_1.csv", index_col=0)

# Inner join on 'State'
merged = pd.merge(df0, df1, on="State", suffixes=('_x', '_y'))

# Rename columns to match target schema exactly (remove suffixes from Participation and Math columns)
merged = merged.rename(columns={
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
})

# Select columns in the exact order of target schema
result = merged[
    ['State', 'Participation_x', 'Evidence-Based Reading and Writing', 'Math_x', 'Total',
     'Participation_y', 'English', 'Math_y', 'Reading', 'Science', 'Composite']
]

# Convert data types to match target schema
result = result.astype({
    'Participation_x': 'string',
    'Participation_y': 'string',
    'Evidence-Based Reading and Writing': 'Int64',
    'Math_x': 'Int64',
    'Total': 'Int64',
    'English': 'float',
    'Math_y': 'float',
    'Reading': 'float',
    'Science': 'float',
    'Composite': 'float'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts.csv", index=False)