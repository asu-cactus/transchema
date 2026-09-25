import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

# Normalize city names in both sources: strip and lowercase
df0['city'] = df0['city'].str.strip().str.lower()
df1['city'] = df1['city'].str.strip().str.lower()

# Aggregate Source0 by city
agg = df0.groupby('city').agg({'fare': 'mean', 'ride_id': 'count'}).reset_index()
agg.rename(columns={'fare': 'Average Fare ($)', 'ride_id': 'Number of Rides', 'city': 'city'}, inplace=True)

# Join aggregated Source0 with Source1 on city
joined = pd.merge(agg, df1, how='inner', on='city')

# Rename columns to match target schema
joined.rename(columns={'city': 'City', 'driver_count': 'Number of Drivers', 'type': 'City Type'}, inplace=True)

# Group by City, Number of Drivers, City Type to ensure unique rows (in case of duplicates)
result = joined.groupby(['City', 'Number of Drivers', 'City Type'], as_index=False).agg({
    'Average Fare ($)': 'mean',
    'Number of Rides': 'mean'
})

# Cast columns to correct types
result['Number of Drivers'] = result['Number of Drivers'].astype('Int64')
result['Average Fare ($)'] = result['Average Fare ($)'].astype(float)
result['Number of Rides'] = result['Number of Rides'].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)