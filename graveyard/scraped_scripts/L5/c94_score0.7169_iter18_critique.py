import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_94/training_1.csv", index_col=0)

# Join on 'city'
merged = pd.merge(source1, source0, on='city', how='inner')

# Group by city and type (City Type)
agg = merged.groupby(['city', 'type'], as_index=False).agg(
    **{
        'Average Fare': ('fare', 'mean'),
        'ride_id': ('ride_id', 'max'),
        'Total Number of Rides': ('ride_id', 'count'),
        'Total Number of Drivers': ('driver_count', 'sum')
    }
)

# Rename columns to match target schema
agg = agg.rename(columns={
    'city': 'City',
    'type': 'City Type'
})

# Reorder columns as per target schema
agg = agg[['City', 'Average Fare', 'ride_id', 'Total Number of Rides', 'City Type', 'Total Number of Drivers']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_94/target_multisource_mcts.csv", index=False)