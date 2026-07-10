import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Rename columns in each source to match target schema naming
df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Join on 'State'
result = pd.merge(df0_renamed, df1_renamed, on='State', how='inner')

# Convert integer columns to integer type as in target
result['Evidence-Based Reading and Writing'] = result['Evidence-Based Reading and Writing'].astype('Int64')
result['Math_y'] = result['Math_y'].astype('Int64')
result['Total'] = result['Total'].astype('Int64')

# Reorder columns exactly as target schema
cols = ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
        'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)