import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(source0, source1, on='city', how='inner')

# Group by city, driver_count, type and aggregate fare and ride_id
agg = merged.groupby(['city', 'driver_count', 'type'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': 'count'
})

# Rename columns to match target schema
agg.rename(columns={
    'city': 'City',
    'fare': 'Average Fare ($)',
    'ride_id': 'Number of Rides',
    'driver_count': 'Number of Drivers',
    'type': 'City Type'
}, inplace=True)

# Cast types as per target schema
agg = agg.astype({
    'City': str,
    'Average Fare ($)': float,
    'Number of Rides': float,
    'Number of Drivers': int,
    'City Type': str
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)