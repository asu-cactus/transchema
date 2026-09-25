import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv', index_col=0)

merged = pd.merge(df0, df1, on='city', how='inner')

agg = merged.groupby(['city', 'type'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'max',
    'driver_count': 'max',
    'ride_id': ['max', 'count']  # We need max and count of ride_id, but 'max' is already used above, so we must separate
})

# The above agg dict is invalid because 'ride_id' appears twice.
# So we do aggregation in two steps or use named aggregation (pandas >= 0.25)

agg = merged.groupby(['city', 'type'], as_index=False).agg(
    Average_Fare=('fare', 'mean'),
    Max_Ride_ID=('ride_id', 'max'),
    Total_Number_of_Rides=('ride_id', 'count'),
    Total_Number_of_Drivers=('driver_count', 'max')
)

# Rename columns to match target schema exactly
agg = agg.rename(columns={
    'city': 'City',
    'type': 'City Type',
    'Average_Fare': 'Average Fare',
    'Max_Ride_ID': 'ride_id',
    'Total_Number_of_Rides': 'Total Number of Rides',
    'Total_Number_of_Drivers': 'Total Number of Drivers'
})

# Convert ride_id to float as in target examples
agg['ride_id'] = agg['ride_id'].astype(float)
agg['Total Number of Rides'] = agg['Total Number of Rides'].astype(int)
agg['Total Number of Drivers'] = agg['Total Number of Drivers'].astype(int)

agg.to_csv('autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv', index=False)