import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_51/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_51/training_1.csv", index_col=0)

grouped = source0.groupby('city').agg({'ride_id':'count', 'fare':'mean'}).reset_index()
grouped.rename(columns={'ride_id':'Ride Count', 'fare':'Average Fare'}, inplace=True)

merged = pd.merge(source1, grouped, on='city', how='inner')

result = merged[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_51/target_multisource_mcts.csv", index=False)