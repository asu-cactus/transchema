import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_1.csv", index_col=0)

groupby_result = df1.groupby('city', as_index=False).agg({'ride_id':'count'}).rename(columns={'ride_id':'ride_id_count'})

joined = pd.merge(df1, groupby_result[['city']], on='city', how='inner')

result = joined[['city', 'ride_id']].copy()
result['ride_id'] = result['ride_id'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_5/target_multisource_mcts.csv", index=False)