import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_3.csv", index_col=0)

# Rename columns to include year suffixes matching target schema
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

# Join all tables on 'Wrestler' using outer joins to keep all wrestlers
df_join = df0.merge(df1, on='Wrestler', how='outer') \
             .merge(df2, on='Wrestler', how='outer') \
             .merge(df3, on='Wrestler', how='outer')

# Fill NaN values with 0 for numeric columns (missing means no matches)
for col in df_join.columns:
    if col != 'Wrestler':
        df_join[col] = df_join[col].fillna(0).astype(int)

# Reorder columns exactly as target schema
cols = ['Wrestler',
        '2013 Wins', '2013 Losses', '2013 Draws',
        '2014 Wins', '2014 Losses', '2014 Draws',
        '2015 Wins', '2015 Losses', '2015 Draws',
        '2016 Wins', '2016 Losses', '2016 Draws']

df_join = df_join.reindex(columns=cols)

# Write output
df_join.to_csv("autopipeline-benchmarks/github-pipelines/length3_68/target_multisource_mcts.csv", index=False)