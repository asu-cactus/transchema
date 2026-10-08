import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_28/training_1.csv", index_col=0)

union_result = pd.concat([source0, source0], ignore_index=True)

grouped_source0 = union_result.groupby('city', as_index=False).agg({'driver_count':'sum', 'type':'first'})

joined = pd.merge(grouped_source0, source1, on='city', how='inner')

agg = joined.groupby(['city', 'type'], as_index=False).agg(
    driver_count=('driver_count', 'first'),
    Average_Fare=('fare', 'mean'),
    Ride_Count=('ride_id', 'count')
)

agg = agg.rename(columns={'Average_Fare': 'Average Fare', 'Ride_Count': 'Ride Count'})

agg = agg[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

agg['driver_count'] = agg['driver_count'].astype(int)
agg['Ride Count'] = agg['Ride Count'].astype(int)
agg['type'] = agg['type'].astype(str)
agg['city'] = agg['city'].astype(str)
agg['Average Fare'] = agg['Average Fare'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_28/target_multisource_mcts.csv", index=False)