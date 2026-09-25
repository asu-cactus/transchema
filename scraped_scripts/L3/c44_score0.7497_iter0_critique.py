import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_44/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_44/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(source0, source1, how='inner', on='city')

# Group by city, driver_count, type and aggregate
agg = joined.groupby(['city', 'driver_count', 'type']).agg({'fare':'mean', 'ride_id':'count'}).reset_index()

# Rename columns to match target schema
agg = agg.rename(columns={'fare':'Average Fare', 'ride_id':'Ride Count'})

# Ensure correct types
agg['driver_count'] = agg['driver_count'].astype(int)
agg['Ride Count'] = agg['Ride Count'].astype(int)
agg['Average Fare'] = agg['Average Fare'].astype(float)
agg['city'] = agg['city'].astype(str)
agg['type'] = agg['type'].astype(str)

# Reorder columns as per target schema
agg = agg[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_44/target_multisource_mcts.csv", index=False)