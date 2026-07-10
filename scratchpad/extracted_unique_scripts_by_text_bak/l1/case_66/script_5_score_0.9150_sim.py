import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_66/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_66/training_1.csv", index_col=0)

df0 = df0.rename(columns={'Participation': 'Participation_x', 'Math': 'Math_x'})
df1 = df1.rename(columns={'Participation': 'Participation_y', 'Math': 'Math_y'})

df_merged = pd.merge(df0, df1, on='State', how='inner')

df_merged = df_merged[['State', 'Participation_x', 'Evidence-Based Reading and Writing', 'Math_x', 'Total',
                       'Participation_y', 'English', 'Math_y', 'Reading', 'Science', 'Composite']]

df_merged['Evidence-Based Reading and Writing'] = pd.to_numeric(df_merged['Evidence-Based Reading and Writing'], errors='coerce').astype('Int64')
df_merged['Math_x'] = pd.to_numeric(df_merged['Math_x'], errors='coerce').astype('Int64')
df_merged['Total'] = pd.to_numeric(df_merged['Total'], errors='coerce').astype('Int64')
df_merged['English'] = pd.to_numeric(df_merged['English'], errors='coerce')
df_merged['Math_y'] = pd.to_numeric(df_merged['Math_y'], errors='coerce')
df_merged['Reading'] = pd.to_numeric(df_merged['Reading'], errors='coerce')
df_merged['Science'] = pd.to_numeric(df_merged['Science'], errors='coerce')
df_merged['Composite'] = pd.to_numeric(df_merged['Composite'], errors='coerce')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_66/target_multisource_mcts.csv", index=False)