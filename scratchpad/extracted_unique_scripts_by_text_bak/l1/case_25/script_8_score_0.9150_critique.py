import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

# Rename columns in df1 to match target schema suffixes before merge to avoid suffixes added by merge
df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math': 'Math_y',
    'Total': 'Total'
})

# Rename columns in df0 to match target schema suffixes before merge
df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

# Merge on State with inner join (default)
df = pd.merge(df0, df1, on='State', how='inner')

# Select columns in exact order as target schema
df = df[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
         'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Cast columns to target types if needed
df['Participation_x'] = df['Participation_x'].astype(str)
df['Participation_y'] = df['Participation_y'].astype(str)
df['English'] = df['English'].astype(float)
df['Math_x'] = df['Math_x'].astype(float)
df['Reading'] = df['Reading'].astype(float)
df['Science'] = df['Science'].astype(float)
df['Composite'] = df['Composite'].astype(float)
df['Evidence-Based Reading and Writing'] = df['Evidence-Based Reading and Writing'].astype(int)
df['Math_y'] = df['Math_y'].astype(int)
df['Total'] = df['Total'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)