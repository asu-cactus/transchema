import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

df_merged = pd.merge(df0_renamed, df1_renamed, on='State', how='outer')

df_merged['Evidence-Based Reading and Writing'] = pd.to_numeric(df_merged['Evidence-Based Reading and Writing'], errors='coerce').astype('Int64')
df_merged['Total'] = pd.to_numeric(df_merged['Total'], errors='coerce').astype('Int64')

cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

df_final = df_merged[cols]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)