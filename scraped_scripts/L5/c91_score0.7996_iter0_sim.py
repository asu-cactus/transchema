import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_91/training_4.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

agg = df.groupby('longitude').agg({
    'missing_count': 'max',
    'state': lambda x: pd.to_numeric(x, errors='coerce').max() if pd.api.types.is_numeric_dtype(x) else x.mode().iloc[0] if not x.mode().empty else None,
    'latitude': 'max'
}).reset_index()

# The target schema requires 'state' and 'latitude' as integers, 'missing_count' as integer, 'longitude' as float
# 'state' column in sources is string, but target expects integer, so convert state strings to integer codes
agg['state'] = pd.Categorical(agg['state']).codes
agg['missing_count'] = agg['missing_count'].astype(int)
agg['state'] = agg['state'].astype(int)
agg['latitude'] = agg['latitude'].astype(int)
agg['longitude'] = agg['longitude'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_91/target_multisource_mcts.csv", index=False)