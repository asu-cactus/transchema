import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv"

# Read source tables with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Rename columns to match target schema exactly
# Source0 columns: ['State', 'Participation', 'English', 'Math', 'Reading', 'Science', 'Composite']
# Source1 columns: ['State', 'Participation', 'Evidence-Based Reading and Writing', 'Math', 'Total']
# Target columns: ['State', 'Participation_x', 'English', 'Math_x', 'Reading', 'Science', 'Composite',
#                  'Participation_y', 'Evidence-Based Reading and Writing', 'Math_y', 'Total']

df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Join on 'State' with inner join to keep only states present in both sources
df_merged = pd.merge(df0_renamed, df1_renamed, on='State', how='inner')

# Select and reorder columns to match target schema exactly
target_columns = [
    'State',
    'Participation_x',
    'English',
    'Math_x',
    'Reading',
    'Science',
    'Composite',
    'Participation_y',
    'Evidence-Based Reading and Writing',
    'Math_y',
    'Total'
]

df_final = df_merged[target_columns]

# Cast columns to correct types as per target schema
df_final['Participation_x'] = df_final['Participation_x'].astype(str)
df_final['Participation_y'] = df_final['Participation_y'].astype(str)

df_final['English'] = df_final['English'].astype(float)
df_final['Math_x'] = df_final['Math_x'].astype(float)
df_final['Reading'] = df_final['Reading'].astype(float)
df_final['Science'] = df_final['Science'].astype(float)
df_final['Composite'] = df_final['Composite'].astype(float)

df_final['Evidence-Based Reading and Writing'] = df_final['Evidence-Based Reading and Writing'].astype(int)
df_final['Math_y'] = df_final['Math_y'].astype(int)
df_final['Total'] = df_final['Total'].astype(int)

# Write output CSV without index
df_final.to_csv(output_path, index=False)