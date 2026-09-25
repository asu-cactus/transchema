import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_3.csv", index_col=0)

# Rename columns to match target schema
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

# Join all four dataframes on 'Wrestler'
df_joined = df0.merge(df1, on='Wrestler', how='inner') \
               .merge(df2, on='Wrestler', how='inner') \
               .merge(df3, on='Wrestler', how='inner')

# Ensure correct column order as per target schema
cols_order = ['Wrestler',
              '2013 Wins', '2013 Losses', '2013 Draws',
              '2014 Wins', '2014 Losses', '2014 Draws',
              '2015 Wins', '2015 Losses', '2015 Draws',
              '2016 Wins', '2016 Losses', '2016 Draws']

df_joined = df_joined.reindex(columns=cols_order)

# Convert all numeric columns to int (in case of any float)
for col in cols_order[1:]:
    df_joined[col] = pd.to_numeric(df_joined[col], errors='coerce').fillna(0).astype(int)

# Write output
df_joined.to_csv("autopipeline-benchmarks/github-pipelines/length3_23/target_multisource_mcts.csv", index=False)