import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_1.csv", index_col=0)

agg0 = source0.groupby('city').agg(
    Average_Fare=('fare', 'min'),
    Ride_Count=('ride_id', 'count')
).reset_index()

agg1 = source1.groupby(['city', 'type']).agg(
    driver_count=('driver_count', 'sum')
).reset_index()

merged = pd.merge(agg0, agg1, how='inner', on='city')
final = merged[merged['type'].notna()]

final = final[['city', 'driver_count', 'type', 'Average_Fare', 'Ride_Count']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_50/target_multisource_mcts.csv", index=False)