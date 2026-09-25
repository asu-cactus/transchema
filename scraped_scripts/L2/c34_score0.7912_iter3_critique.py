import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_34/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_34/training_1.csv', index_col=0)

# Join on 'city'
df_joined = pd.merge(df0, df1, on='city', how='inner')

# Group by 'city' and count ride_id occurrences
df_result = df_joined.groupby('city', as_index=False).agg({'ride_id': 'count'})

# Ensure ride_id is integer type
df_result['ride_id'] = df_result['ride_id'].astype(int)

df_result.to_csv('autopipeline-benchmarks/github-pipelines/length2_34/target_multisource_mcts.csv', index=False)