import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_18/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_18/training_1.csv", index_col=0)

# Join on 'city'
df = pd.merge(df0, df1, on='city', how='inner')

# Group by 'city', aggregate fare by mean, ride_id by count
result = df.groupby('city', as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'count'
})

# Rename 'ride_id' count to integer type (count is int64 by default)
result['ride_id'] = result['ride_id'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_18/target_multisource_mcts.csv", index=False)