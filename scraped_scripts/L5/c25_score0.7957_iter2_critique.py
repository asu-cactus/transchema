import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_25/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_25/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Ensure correct types
df['longitude'] = df['longitude'].astype(float)
df['missing_count'] = df['missing_count'].astype(int)
df['state'] = df['state'].astype(str)
df['latitude'] = df['latitude'].astype(float)

# Group by longitude
agg_df = df.groupby('longitude').agg(
    missing_count=('missing_count', 'sum'),
    state=('state', pd.Series.nunique),
    latitude=('latitude', pd.Series.nunique)
).reset_index()

# Convert aggregated columns to int as per target schema
agg_df['missing_count'] = agg_df['missing_count'].astype(int)
agg_df['state'] = agg_df['state'].astype(int)
agg_df['latitude'] = agg_df['latitude'].astype(int)

# Reorder columns to match target schema
agg_df = agg_df[['longitude', 'missing_count', 'state', 'latitude']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_25/target_multisource_mcts.csv", index=False)