import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_df1 = df1.groupby('city').agg(
    Average_Fare=('fare', 'mean'),
    ride_id=('ride_id', 'mean'),
    Total_Number_of_Rides=('ride_id', 'count')
).reset_index()

merged = pd.merge(df0, agg_df1, left_on='city', right_on='city', how='inner')

result = merged.rename(columns={
    'city': 'City',
    'type': 'City Type',
    'driver_count': 'Total Number of Drivers',
    'Average_Fare': 'Average Fare',
    'ride_id': 'ride_id',
    'Total_Number_of_Rides': 'Total Number of Rides'
})

result = result[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

result.to_csv(target_path, index=False)