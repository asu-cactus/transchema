import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_58/training_1.csv", index_col=0)

df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

merged = pd.merge(df0, df1, on='State', how='inner')

merged['Participation_x'] = merged['Participation_x'].astype(str)
merged['Participation_y'] = merged['Participation_y'].astype(str)

merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype(int)
merged['Math_x'] = merged['Math_x'].astype(int)
merged['Total'] = merged['Total'].astype(int)

merged['English'] = merged['English'].astype(float)
merged['Math_y'] = merged['Math_y'].astype(float)
merged['Reading'] = merged['Reading'].astype(float)
merged['Science'] = merged['Science'].astype(float)
merged['Composite'] = merged['Composite'].astype(float)

target_cols = ['State', 'Participation_x', 'Evidence-Based Reading and Writing', 'Math_x', 'Total',
               'Participation_y', 'English', 'Math_y', 'Reading', 'Science', 'Composite']

result = merged[target_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_58/target_multisource_mcts.csv", index=False)