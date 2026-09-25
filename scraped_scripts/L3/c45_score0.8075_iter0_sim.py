import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_45/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_45/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_45/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df0.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    Ride_Count=('ride_id', 'count')
).reset_index()

merged = pd.merge(df1, agg, on='city', how='inner')

merged = merged.rename(columns={
    'Average_Fare': 'Average Fare',
    'Ride_Count': 'Ride Count'
})

merged = merged[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

merged.to_csv(target_path, index=False)