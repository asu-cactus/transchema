import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_1.csv", index_col=0)

# Rename only the overlapping columns to match target schema
df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Join on 'State'
df_merged = pd.merge(df0, df1, on='State', how='inner')

# Reorder columns to match target schema exactly
df_merged = df_merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                       'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Cast columns to correct types as per target schema
df_merged['Participation_x'] = df_merged['Participation_x'].astype(str)
df_merged['Participation_y'] = df_merged['Participation_y'].astype(str)

df_merged['English'] = df_merged['English'].astype(float)
df_merged['Math_x'] = df_merged['Math_x'].astype(float)
df_merged['Reading'] = df_merged['Reading'].astype(float)
df_merged['Science'] = df_merged['Science'].astype(float)
df_merged['Composite'] = df_merged['Composite'].astype(float)

df_merged['Evidence-Based Reading and Writing'] = pd.to_numeric(df_merged['Evidence-Based Reading and Writing'], errors='coerce').astype('Int64')
df_merged['Math_y'] = pd.to_numeric(df_merged['Math_y'], errors='coerce').astype('Int64')
df_merged['Total'] = pd.to_numeric(df_merged['Total'], errors='coerce').astype('Int64')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_63/target_multisource_mcts.csv", index=False)