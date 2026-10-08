import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_68/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_68/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_68/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_68/training_3.csv"
]

# Read each source with index_col=0 to ignore the first index column
df0 = pd.read_csv(paths[0], index_col=0)
df1 = pd.read_csv(paths[1], index_col=0)
df2 = pd.read_csv(paths[2], index_col=0)
df3 = pd.read_csv(paths[3], index_col=0)

# Rename columns to include year suffix as per target schema
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

# Join all dataframes on 'Wrestler' using inner join to keep only wrestlers present in all years
df_merged = df0.merge(df1, on='Wrestler', how='inner') \
               .merge(df2, on='Wrestler', how='inner') \
               .merge(df3, on='Wrestler', how='inner')

# Ensure correct column order as per target schema
target_columns = [
    'Wrestler',
    '2013 Wins', '2013 Losses', '2013 Draws',
    '2014 Wins', '2014 Losses', '2014 Draws',
    '2015 Wins', '2015 Losses', '2015 Draws',
    '2016 Wins', '2016 Losses', '2016 Draws'
]

df_merged = df_merged[target_columns]

# Convert all numeric columns to int (if any NaNs, fill with 0)
num_cols = target_columns[1:]
df_merged[num_cols] = df_merged[num_cols].fillna(0).astype(int)

# Write to output CSV
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_68/target_multisource_mcts.csv", index=False)