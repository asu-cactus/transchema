import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Rename columns to match target schema exactly
df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# INNER JOIN on 'State' to keep only states present in both sources
df_merged = pd.merge(df0_renamed, df1_renamed, on='State', how='inner')

# Reorder columns to match target schema exactly
df_merged = df_merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                       'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

# Convert integer columns to Int64 dtype to match target examples
df_merged['Evidence-Based Reading and Writing'] = pd.to_numeric(df_merged['Evidence-Based Reading and Writing'], errors='coerce').astype('Int64')
df_merged['Math_y'] = pd.to_numeric(df_merged['Math_y'], errors='coerce').astype('Int64')
df_merged['Total'] = pd.to_numeric(df_merged['Total'], errors='coerce').astype('Int64')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)