import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_25/training_1.csv", index_col=0)

# Ensure Participation columns are strings with % sign, no aggregation
df0['Participation'] = df0['Participation'].astype(str)
df1['Participation'] = df1['Participation'].astype(str)

# Rename columns to match target schema exactly
df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Join on State
result = pd.merge(df0_renamed, df1_renamed, on='State', how='inner')

# Convert numeric columns to correct types
result['English'] = result['English'].astype(float)
result['Math_x'] = result['Math_x'].astype(float)
result['Reading'] = result['Reading'].astype(float)
result['Science'] = result['Science'].astype(float)
result['Composite'] = result['Composite'].astype(float)

result['Evidence-Based Reading and Writing'] = result['Evidence-Based Reading and Writing'].astype('Int64')
result['Math_y'] = result['Math_y'].astype('Int64')
result['Total'] = result['Total'].astype('Int64')

# Select columns in target schema order
result = result[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_25/target_multisource_mcts.csv", index=False)