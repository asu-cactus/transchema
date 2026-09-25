import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_1.csv", index_col=0)

agg = df1.groupby(['city', 'ride_id'], as_index=False).agg(
    fare_min=('fare', 'min'),
    fare_max=('fare', 'max'),
    fare_avg=('fare', 'mean')
)

result = agg[['city', 'ride_id']].copy()
result['ride_id'] = result['ride_id'].astype(int)
result['city'] = result['city'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_75/target_multisource_mcts.csv", index=False)