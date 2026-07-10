import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_44/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_44/training_1.csv", index_col=0)

agg = source0.groupby('city').agg({'ride_id':'count', 'fare':'mean'}).reset_index()
agg = agg.rename(columns={'ride_id':'Ride Count', 'fare':'Average Fare'})

joined = pd.merge(source1, agg, how='inner', on='city')

joined = joined.rename(columns={'city':'city', 'driver_count':'driver_count', 'type':'type'})

joined = joined[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

joined['driver_count'] = joined['driver_count'].astype(int)
joined['Ride Count'] = joined['Ride Count'].astype(int)
joined['Average Fare'] = joined['Average Fare'].astype(float)
joined['city'] = joined['city'].astype(str)
joined['type'] = joined['type'].astype(str)

joined.to_csv("autopipeline-benchmarks/github-pipelines/length3_44/target_multisource_mcts.csv", index=False)