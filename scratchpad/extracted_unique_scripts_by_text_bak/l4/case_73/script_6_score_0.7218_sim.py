import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

agg_source0 = source0.groupby('city').agg({'fare':'mean', 'ride_id':'count'}).reset_index()
agg_source0.rename(columns={'fare':'mean_fare', 'ride_id':'count_ride_id'}, inplace=True)

merged = pd.merge(agg_source0, source1, on='city', how='inner')

merged.rename(columns={
    'city':'City',
    'mean_fare':'Average Fare ($)',
    'count_ride_id':'Number of Rides',
    'driver_count':'Number of Drivers',
    'type':'City Type'
}, inplace=True)

merged = merged.astype({
    'City': str,
    'Average Fare ($)': float,
    'Number of Rides': float,
    'Number of Drivers': int,
    'City Type': str
})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)