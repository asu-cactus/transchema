import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv", index_col=0)

# Join on 'State' with inner join to keep only states present in both sources
merged = pd.merge(df0, df1, on='State', how='inner', suffixes=('_x', '_y'))

# Rename columns to match target schema exactly
# Participation columns already have suffixes from merge
# Rename 'Evidence-Based Reading and Writing' to exact target name (no change)
# Rename 'Math_x' and 'Math_y' are already correct due to suffixes
# Ensure types match target schema: Participation_x and Participation_y as string,
# Evidence-Based Reading and Writing, Math_y, Total as integers

merged['Participation_x'] = merged['Participation_x'].astype(str)
merged['Participation_y'] = merged['Participation_y'].astype(str)
merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype('Int64')
merged['Math_y'] = merged['Math_y'].astype('Int64')
merged['Total'] = merged['Total'].astype('Int64')

# Select columns in target schema order
result = merged[['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
                 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv", index=False)