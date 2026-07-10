import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Rename columns in df1 to match target schema exactly
df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Evidence-Based Reading and Writing': 'Evidence-Based Reading and Writing',
    'Math': 'Math_y',
    'Total': 'Total'
})

# Rename columns in df0 to match target schema exactly
df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

# Join on State with inner join to keep only states present in both sources
df_final = pd.merge(df0, df1, how='inner', on='State')

# Select columns in the exact order as target schema
df_final = df_final[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                     'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)