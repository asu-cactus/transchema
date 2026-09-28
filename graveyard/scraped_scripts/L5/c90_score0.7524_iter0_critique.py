import pandas as pd

# Read sources with index_col=0 as instructed
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv", index_col=0)

# Normalize city names in both dataframes: strip and lower to ensure join matches
df0['city'] = df0['city'].str.strip().str.lower()
df1['city'] = df1['city'].str.strip().str.lower()

# Aggregate df0 by city
agg = df0.groupby('city').agg({
    'fare': 'mean',
    'ride_id': ['max', 'count']
}).reset_index()

# Flatten multiindex columns
agg.columns = ['city', 'Average Fare', 'ride_id', 'Total Number of Rides']

# Join with df1 on city
merged = pd.merge(agg, df1, how='inner', on='city')

# Rename columns to match target schema
merged = merged.rename(columns={
    'city': 'City',
    'type': 'City Type',
    'driver_count': 'Total Number of Drivers'
})

# Cast types as per target schema
merged['Total Number of Rides'] = merged['Total Number of Rides'].astype(int)
merged['Total Number of Drivers'] = merged['Total Number of Drivers'].astype(int)
merged['Average Fare'] = merged['Average Fare'].astype(float)
merged['ride_id'] = merged['ride_id'].astype(float)

# Select columns in target order
result = merged[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv", index=False)