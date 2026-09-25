import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv", index_col=0)

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
df = df0.merge(df1, on='Wrestler', how='inner') \
        .merge(df2, on='Wrestler', how='inner') \
        .merge(df3, on='Wrestler', how='inner')

# Ensure integer type for all numeric columns
for col in df.columns:
    if col != 'Wrestler':
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)