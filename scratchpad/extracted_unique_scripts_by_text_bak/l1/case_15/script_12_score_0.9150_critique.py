import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_15/training_1.csv", index_col=0)

# Join on 'State'
merged = pd.merge(df0, df1, on='State', suffixes=('_x', '_y'))

# Rename columns to exactly match target schema
# Target schema: ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite', 'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

# Participation columns are already suffixed by merge
# Just reorder columns to match target schema
merged = merged[['State', 
                 'Participation_x', 
                 'English', 
                 'Math_x', 
                 'Reading', 
                 'Science', 
                 'Composite', 
                 'Participation_y', 
                 'Evidence-Based Reading and Writing', 
                 'Math_y', 
                 'Total']]

# Convert integer columns to integer type
merged['Evidence-Based Reading and Writing'] = merged['Evidence-Based Reading and Writing'].astype('Int64')
merged['Math_y'] = merged['Math_y'].astype('Int64')
merged['Total'] = merged['Total'].astype('Int64')

# Write output
merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_15/target_multisource_mcts.csv", index=False)