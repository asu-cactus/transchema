import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(df0, df1, how='inner', left_on='city', right_on='city')

# Group by city and aggregate
agg = joined.groupby('city').agg({
    'fare': 'mean',
    'ride_id': 'count',
    'driver_count': 'max',
    'type': 'first'
}).reset_index()

# Rename columns to match target schema
agg = agg.rename(columns={
    'city': 'City',
    'fare': 'Average Fare ($)',
    'ride_id': 'Number of Rides',
    'driver_count': 'Number of Drivers',
    'type': 'City Type'
})

# Convert Number of Drivers to integer type
agg['Number of Drivers'] = agg['Number of Drivers'].astype('Int64')

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)