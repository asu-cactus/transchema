import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_39/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_39/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length1_39/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Rename columns in df0 to match target schema suffixes for clarity before pivot
df0_renamed = df0.rename(columns={
    'Participation': 'Participation_x',
    'Math': 'Math_x'
})

# Pivot df0 on Participation_x to create Participation_y dimension
# Actually, the partial plan says PIVOT on Participation_y, but df0 has Participation_x only.
# The target has both Participation_x and Participation_y.
# Participation_y comes from df1 Participation column.
# So we keep df0 as is with Participation_x, and df1 has Participation_y.

# No pivot needed on df0, but we keep Participation_x as is.
# The partial plan suggests pivot on Participation_y, which is from df1.
# So we pivot df1 on Participation to get Participation_y as columns? But target schema has Participation_y as a column, not multiple columns.
# So no pivot needed, just rename Participation in df1 to Participation_y.

df1_renamed = df1.rename(columns={
    'Participation': 'Participation_y',
    'Math': 'Math_y'
})

# Join df0 and df1 on State
df_merged = pd.merge(df0_renamed, df1_renamed, on='State', how='inner')

# Reorder and select columns to match target schema
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

# Fix data types according to target schema
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

df_final.to_csv(output_path, index=False)