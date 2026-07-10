import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_0.csv", index_col=0)  # 2016
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_1.csv", index_col=0)  # 2013
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_2.csv", index_col=0)  # 2015
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_3.csv", index_col=0)  # 2014

# Rename columns to match target schema for each year
df1 = df1.rename(columns={
    'Wins': '2013 Wins',
    'Losses': '2013 Losses',
    'Draws': '2013 Draws'
})

df3 = df3.rename(columns={
    'Wins': '2014 Wins',
    'Losses': '2014 Losses',
    'Draws': '2014 Draws'
})

df2 = df2.rename(columns={
    'Wins': '2015 Wins',
    'Losses': '2015 Losses',
    'Draws': '2015 Draws'
})

df0 = df0.rename(columns={
    'Wins': '2016 Wins',
    'Losses': '2016 Losses',
    'Draws': '2016 Draws'
})

# Merge all dataframes on Wrestler using outer join to keep all wrestlers
df_merge = pd.merge(df1, df3, on='Wrestler', how='outer')
df_merge = pd.merge(df_merge, df2, on='Wrestler', how='outer')
df_merge = pd.merge(df_merge, df0, on='Wrestler', how='outer')

# Fill NaN with 0 for numeric columns (missing data means zero wins/losses/draws)
for col in df_merge.columns:
    if col != 'Wrestler':
        df_merge[col] = df_merge[col].fillna(0).astype(int)

# Reorder columns to match target schema exactly
cols = ['Wrestler',
        '2013 Wins', '2013 Losses', '2013 Draws',
        '2014 Wins', '2014 Losses', '2014 Draws',
        '2015 Wins', '2015 Losses', '2015 Draws',
        '2016 Wins', '2016 Losses', '2016 Draws']

df_final = df_merge[cols]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_7/target_multisource_mcts.csv", index=False)