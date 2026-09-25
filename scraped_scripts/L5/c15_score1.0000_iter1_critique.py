import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_4.csv", index_col=0)

# UNION all sources
all_sources = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

# Convert 'state' to categorical codes (integer)
all_sources['state'] = all_sources['state'].astype('category').cat.codes

# Convert latitude to integer
all_sources['latitude'] = all_sources['latitude'].astype(int)

# missing_count is integer already
all_sources['missing_count'] = all_sources['missing_count'].astype(int)

# longitude is float already
all_sources['longitude'] = all_sources['longitude'].astype(float)

# Group by 'state'
grouped = all_sources.groupby('state').agg(
    missing_count=('missing_count', 'count'),
    longitude=('longitude', 'mean'),
    latitude=('latitude', 'mean')
).reset_index()

# Convert latitude to int after mean
grouped['latitude'] = grouped['latitude'].astype(int)

# Reorder columns to target schema: ['longitude', 'missing_count', 'state', 'latitude']
target = grouped[['longitude', 'missing_count', 'state', 'latitude']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_15/target_multisource_mcts.csv", index=False)