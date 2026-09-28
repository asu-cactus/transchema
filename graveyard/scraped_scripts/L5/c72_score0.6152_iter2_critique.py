import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_72/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_72/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_72/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_72/training_4.csv", index_col=0)

df1 = df1.rename(columns={'missing_count': 'missing_count_1', 'latitude': 'latitude_1', 'longitude': 'longitude_1'})
df2 = df2.rename(columns={'missing_count': 'missing_count_2', 'latitude': 'latitude_2', 'longitude': 'longitude_2'})
df3 = df3.rename(columns={'missing_count': 'missing_count_3', 'latitude': 'latitude_3', 'longitude': 'longitude_3'})
df4 = df4.rename(columns={'missing_count': 'missing_count_4', 'latitude': 'latitude_4', 'longitude': 'longitude_4'})

df_join = df0.merge(df1, on='state', how='inner') \
             .merge(df2, on='state', how='inner') \
             .merge(df3, on='state', how='inner') \
             .merge(df4, on='state', how='inner')

df_join['missing_count'] = (df_join['missing_count'] + df_join['missing_count_1'] + df_join['missing_count_2'] +
                            df_join['missing_count_3'] + df_join['missing_count_4'])

df_join['latitude'] = df_join['latitude'].round().astype(int)
df_join['longitude'] = df_join['longitude'].round().astype(int)

result = df_join[['state', 'missing_count', 'latitude', 'longitude']]
result['missing_count'] = result['missing_count'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_72/target_multisource_mcts.csv", index=False)