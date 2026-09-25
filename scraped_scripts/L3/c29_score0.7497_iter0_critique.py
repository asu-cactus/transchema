import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_29/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on='city', how='inner')

agg = merged.groupby(['city', 'driver_count', 'type']).agg({'fare':'mean', 'ride_id':'count'}).reset_index()
agg.rename(columns={'fare':'Average Fare', 'ride_id':'Ride Count'}, inplace=True)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_29/target_multisource_mcts.csv", index=False)