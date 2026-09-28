import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

# Rename columns in df0 to match target schema for clarity before join
df0_renamed = df0.rename(columns={
    'city': 'City',
    'type': 'City Type',
    'driver_count': 'Total Number of Drivers'
})

# Join on city
merged = pd.merge(df1, df0_renamed, how='inner', left_on='city', right_on='City')

# Group by City and City Type
grouped = merged.groupby(['City', 'City Type'], as_index=False).agg({
    'fare': 'mean',
    'ride_id': ['max', 'count'],
    'Total Number of Drivers': 'max'
})

# Flatten MultiIndex columns
grouped.columns = ['City', 'City Type', 'Average Fare', 'ride_id', 'Total Number of Rides', 'Total Number of Drivers']

# Cast columns to correct types
grouped['Total Number of Rides'] = grouped['Total Number of Rides'].astype(int)
grouped['Total Number of Drivers'] = grouped['Total Number of Drivers'].astype(int)
grouped['Average Fare'] = grouped['Average Fare'].astype(float)
grouped['ride_id'] = grouped['ride_id'].astype(float)

# Reorder columns to match target schema
result = grouped[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)