import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_15/training_4.csv", index_col=0)

# Join s0 and s2 on state, latitude, longitude (inner join)
joined = pd.merge(s0, s2, how='inner', on=['state', 'latitude', 'longitude'], suffixes=('_0', '_2'))

# The join is not directly needed for final output since schemas are identical and target schema matches source schema
# The target schema is ['longitude': float, 'missing_count': int, 'state': int, 'latitude': int]
# But source 'state' is string, target expects integer, so we need to convert 'state' to integer codes
# Also latitude and missing_count are integers in target, but source latitude is float, so convert latitude to int
# longitude is float, keep as is

# Concatenate all sources (union)
all_sources = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

# Convert 'state' from string to categorical codes (integer)
all_sources['state'] = all_sources['state'].astype('category').cat.codes

# Convert latitude to integer
all_sources['latitude'] = all_sources['latitude'].astype(int)

# Convert missing_count to integer (already int but ensure)
all_sources['missing_count'] = all_sources['missing_count'].astype(int)

# longitude as float (already float)
all_sources['longitude'] = all_sources['longitude'].astype(float)

# Select columns in target order
target = all_sources[['longitude', 'missing_count', 'state', 'latitude']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_15/target_multisource_mcts.csv", index=False)