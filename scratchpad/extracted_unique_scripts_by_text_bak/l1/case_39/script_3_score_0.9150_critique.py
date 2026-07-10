import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Join on 'State' column (inner join to keep only states present in both)
df = pd.merge(df0, df1, on="State", how="inner", suffixes=('_x', '_y'))

# Rename columns to match target schema exactly (no suffixes)
df = df.rename(columns={
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

# Select columns in the exact order of target schema
df = df[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
         'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Cast integer columns to integer type
df['Evidence-Based Reading and Writing'] = df['Evidence-Based Reading and Writing'].astype('Int64')
df['Math_y'] = df['Math_y'].astype('Int64')
df['Total'] = df['Total'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv")