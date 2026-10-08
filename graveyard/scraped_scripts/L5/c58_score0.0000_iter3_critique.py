import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_58/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_58/training_4.csv"
]

# Read each source table separately
df0 = pd.read_csv(paths[0], index_col=0)
df1 = pd.read_csv(paths[1], index_col=0)
df2 = pd.read_csv(paths[2], index_col=0)
df3 = pd.read_csv(paths[3], index_col=0)
df4 = pd.read_csv(paths[4], index_col=0)

# Define aggregation function for each df
def agg_df(df, prefix):
    return df.groupby('Category').agg(
        Nominee_count=('Nominee', 'count'),
        Movie_count=('Movie', 'count'),
        Winner_count=('Winner', lambda x: (x == 'YES').sum())
    ).rename(columns={
        'Nominee_count': f'Nominee_{prefix}',
        'Movie_count': f'Movie_{prefix}',
        'Winner_count': f'Winner_{prefix}'
    }).reset_index()

agg0 = agg_df(df0, '0')
agg1 = agg_df(df1, '1')
agg2 = agg_df(df2, '2')
agg3 = agg_df(df3, '3')
agg4 = agg_df(df4, '4')

# Join all aggregated tables on Category
df_join = agg0.merge(agg1, on='Category', how='inner') \
              .merge(agg2, on='Category', how='inner') \
              .merge(agg3, on='Category', how='inner') \
              .merge(agg4, on='Category', how='inner')

# Map counts to target columns:
# Target schema: ['Category', 'Year', 'Nominee', 'Movie', 'Winner']
# Assign:
# Year = Nominee count from Source5_58_2 (agg2)
# Nominee = Nominee count from Source5_58_0 (agg0)
# Movie = Nominee count from Source5_58_1 (agg1)
# Winner = Nominee count from Source5_58_4 (agg4)

result = pd.DataFrame({
    'Category': df_join['Category'],
    'Year': df_join['Nominee_2'],
    'Nominee': df_join['Nominee_0'],
    'Movie': df_join['Nominee_1'],
    'Winner': df_join['Nominee_4']
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_58/target_multisource_mcts.csv", index=False)