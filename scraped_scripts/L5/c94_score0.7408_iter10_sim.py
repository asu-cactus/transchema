import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby('city').agg(
    ride_id=('ride_id', 'count'),
    Average_Fare=('fare', 'mean')
).reset_index()

joined = pd.merge(df0, agg, how='inner', left_on='city', right_on='city')

result = pd.DataFrame()
result['City'] = joined['city']
result['Average Fare'] = joined['Average_Fare']
result['ride_id'] = joined['ride_id'].astype(float)
result['Total Number of Rides'] = joined['ride_id'].astype(int)
result['City Type'] = joined['type']
result['Total Number of Drivers'] = joined['driver_count'].astype(int)

result.to_csv(target_path, index=False)