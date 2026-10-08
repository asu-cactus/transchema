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

df0_cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite']
df1_cols = ['State', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

df0_sel = df0_renamed[df0_cols]
df1_sel = df1_renamed[df1_cols]

df_merged = pd.merge(df0_sel, df1_sel, on='State', how='outer')

df_merged = df_merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                       'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

df_merged['Evidence-Based Reading and Writing'] = pd.to_numeric(df_merged['Evidence-Based Reading and Writing'], errors='coerce').astype('Int64')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)