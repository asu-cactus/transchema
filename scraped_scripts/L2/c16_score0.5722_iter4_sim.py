import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df1.groupby(['city', 'ride_id'], as_index=False).agg({'fare':'mean'})

joined = pd.merge(df0, grouped, on='city', how='inner')

joined = joined.rename(columns={'fare':'fare', 'ride_id':'ride_id', 'driver_count':'driver_count', 'city':'city'})

joined = joined[['city', 'fare', 'ride_id', 'driver_count']]

joined['fare'] = joined['fare'].astype(float)
joined['ride_id'] = joined['ride_id'].astype(float)
joined['driver_count'] = joined['driver_count'].astype(int)
joined['city'] = joined['city'].astype(str)

joined.to_csv(target_path, index=False)