import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

df0['Year Inducted'] = pd.to_numeric(df0['Year Inducted'], errors='coerce')
df2['Year Inducted'] = pd.to_numeric(df2['Year Inducted'], errors='coerce')
df0['Years Waited'] = pd.to_numeric(df0['Years Waited'], errors='coerce').astype('Int64')
df0['# of Years Nominated'] = pd.to_numeric(df0['# of Years Nominated'], errors='coerce').astype('Int64')
df2['Years Waited'] = pd.to_numeric(df2['Years Waited'], errors='coerce').astype('Int64')
df2['# of Years Nominated'] = pd.to_numeric(df2['# of Years Nominated'], errors='coerce').astype('Int64')
df3['Certified Units (Millions)'] = pd.to_numeric(df3['Certified Units (Millions)'], errors='coerce')

df_merged = df0.merge(df1, on='Artist', how='left')
df_merged = df_merged.merge(df2[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated']], on='Artist', how='left', suffixes=('', '_from2'))
df_merged = df_merged.merge(df3, on='Artist', how='left')

# For columns that appear in both df0 and df2, prefer df0's non-null values, else df2's
for col in ['Year Inducted', 'Years Waited', '# of Years Nominated']:
    col2 = col + '_from2'
    df_merged[col] = df_merged[col].combine_first(df_merged[col2])
    df_merged.drop(columns=[col2], inplace=True)

df_merged = df_merged[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

df_merged['Years Waited'] = df_merged['Years Waited'].astype('Int64')
df_merged['# of Years Nominated'] = df_merged['# of Years Nominated'].astype('Int64')
df_merged['Year Inducted'] = pd.to_numeric(df_merged['Year Inducted'], errors='coerce')

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)