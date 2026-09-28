import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_20/training_4.csv", index_col=0)

union_result = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

agg = union_result.groupby(['state', 'latitude'], as_index=False).agg(
    longitude_count=('longitude', 'count'),
    missing_count_sum=('missing_count', 'sum')
)

agg['longitude'] = agg['longitude_count'].astype(float)
agg['missing_count'] = agg['missing_count_sum'].astype(int)

state_int = pd.factorize(agg['state'])[0]
latitude_int = pd.factorize(agg['latitude'])[0]

result = pd.DataFrame({
    'longitude': agg['longitude'],
    'missing_count': agg['missing_count'],
    'state': state_int,
    'latitude': latitude_int
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_20/target_multisource_mcts.csv", index=False)