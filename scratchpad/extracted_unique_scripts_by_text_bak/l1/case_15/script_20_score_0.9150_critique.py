import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on='State', how='inner', suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
merged = merged.rename(columns={
    'Participation_x': 'Participation_x',
    'English': 'English',
    'Math_x': 'Math_x',
    'Reading': 'Reading',
    'Science': 'Science',
    'Composite': 'Composite',
    'Participation_y': 'Participation_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math_y': 'Math_y',
    'Total': 'Total'
})

# Select columns in target schema order
result = merged[
    ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
     'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']
]

# Convert types to match target examples
result['English'] = result['English'].astype(float)
result['Math_x'] = result['Math_x'].astype(float)
result['Reading'] = result['Reading'].astype(float)
result['Science'] = result['Science'].astype(float)
result['Composite'] = result['Composite'].astype(float)

result['Evidence-Based Reading and Writing'] = result['Evidence-Based Reading and Writing'].astype(int)
result['Math_y'] = result['Math_y'].astype(int)
result['Total'] = result['Total'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)