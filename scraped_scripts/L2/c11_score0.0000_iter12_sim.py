import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby(['city', 'ride_id']).agg(
    driver_count=('date', lambda x: x.nunique()),
    fare=('fare', 'mean')
).reset_index()

merged = pd.merge(df0, agg, how='inner', on='city')

result = merged[['city', 'fare', 'ride_id', 'driver_count']]

result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(float)
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv(target_path, index=False)