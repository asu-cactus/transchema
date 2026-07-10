import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

merged = pd.merge(df0_renamed, df1_renamed, on='State', how='inner')

merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype('Int64')
merged['Math_y'] = merged['Math_y'].astype('Int64')
merged['Total'] = merged['Total'].astype('Int64')

final_cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
              'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = merged[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)