import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_4.csv", index_col=0)

# UNION all sources
df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Convert 'state' to categorical codes (integer)
df['state'] = pd.Categorical(df['state']).codes

# Group by 'state' and aggregate
agg = df.groupby('state').agg({
    'longitude': 'mean',
    'missing_count': 'count',
    'latitude': 'mean'
}).reset_index()

# Rename columns to match target schema order: ['longitude', 'missing_count', 'state', 'latitude']
# 'state' is already present as integer codes
agg = agg.rename(columns={
    'missing_count': 'missing_count',
    'longitude': 'longitude',
    'latitude': 'latitude',
    'state': 'state'
})

# Cast columns to target types
agg['longitude'] = agg['longitude'].astype(float)
agg['missing_count'] = agg['missing_count'].astype(int)
agg['state'] = agg['state'].astype(int)
agg['latitude'] = agg['latitude'].round().astype(int)

# Reorder columns to match target schema exactly
agg = agg[['longitude', 'missing_count', 'state', 'latitude']]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_91/target_multisource_mcts.csv", index=False)