import pandas as pd

# File paths
paths = [
    "autopipeline-benchmarks/github-pipelines/length3_67/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_67/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_67/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_67/training_3.csv"
]

# Read each source with index_col=0 to ignore the first index column
df0 = pd.read_csv(paths[0], index_col=0)
df1 = pd.read_csv(paths[1], index_col=0)
df2 = pd.read_csv(paths[2], index_col=0)
df3 = pd.read_csv(paths[3], index_col=0)

# Rename columns to match target schema for each year
df0 = df0.rename(columns={
    'Wins': '2013 Wins',
    'Losses': '2013 Losses',
    'Draws': '2013 Draws'
})

df1 = df1.rename(columns={
    'Wins': '2014 Wins',
    'Losses': '2014 Losses',
    'Draws': '2014 Draws'
})

df2 = df2.rename(columns={
    'Wins': '2015 Wins',
    'Losses': '2015 Losses',
    'Draws': '2015 Draws'
})

df3 = df3.rename(columns={
    'Wins': '2016 Wins',
    'Losses': '2016 Losses',
    'Draws': '2016 Draws'
})

# Join all dataframes on 'Wrestler'
df_join_01 = pd.merge(df0, df1, on='Wrestler', how='inner')
df_join_012 = pd.merge(df_join_01, df2, on='Wrestler', how='inner')
df_final = pd.merge(df_join_012, df3, on='Wrestler', how='inner')

# Ensure columns are in the exact order as target schema
target_columns = [
    'Wrestler',
    '2013 Wins', '2013 Losses', '2013 Draws',
    '2014 Wins', '2014 Losses', '2014 Draws',
    '2015 Wins', '2015 Losses', '2015 Draws',
    '2016 Wins', '2016 Losses', '2016 Draws'
]

df_final = df_final[target_columns]

# Write to CSV without index
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_67/target_multisource_mcts.csv", index=False)