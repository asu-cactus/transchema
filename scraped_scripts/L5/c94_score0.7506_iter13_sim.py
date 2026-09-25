import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby('city').agg({'fare':'mean', 'ride_id':'count'}).reset_index()
agg.rename(columns={'fare':'Average Fare', 'ride_id':'Total Number of Rides'}, inplace=True)

joined = pd.merge(df0, agg, how='inner', left_on='city', right_on='city')

joined.rename(columns={
    'city': 'City',
    'driver_count': 'Total Number of Drivers',
    'type': 'City Type'
}, inplace=True)

joined['ride_id'] = joined['Total Number of Drivers'].astype(float)

result = joined[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

result.to_csv(target_path, index=False)