import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_63/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema suffixes
df0 = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

# Rename columns in df1 to match target schema suffixes
df1 = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Convert numeric columns in df0 to float (already float in source)
# Participation columns remain strings with % sign, no conversion needed

# Convert numeric columns in df1 to int as per target schema
df1['Evidence-Based Reading and Writing'] = df1['Evidence-Based Reading and Writing'].astype(int)
df1['Math_y'] = df1['Math_y'].astype(int)
df1['Total'] = df1['Total'].astype(int)

# Join on 'State' with inner join
result = pd.merge(df0, df1, on='State', how='inner')

# Select and order columns exactly as target schema
result = result[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_63/target_multisource_mcts.csv", index=False)