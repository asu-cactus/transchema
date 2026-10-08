import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# Join on 'track_id'
df = pd.merge(df1, df0, on='track_id', how='inner')

# Select and reorder columns to match target schema
df = df[['index_track', 'track_id', 'dummy']]

# Ensure correct types
df['index_track'] = pd.to_numeric(df['index_track'], errors='coerce').astype('Int64')
df['track_id'] = pd.to_numeric(df['track_id'], errors='coerce').astype('Int64')
df['dummy'] = pd.to_numeric(df['dummy'], errors='coerce').astype('Int64')

# Fill missing dummy values with 1 (dummy is constant 1 in target)
df['dummy'] = df['dummy'].fillna(1).astype(int)

# Group by index_track to ensure uniqueness (if duplicates exist)
df_result = df.groupby('index_track', dropna=False, as_index=False).agg({
    'track_id': 'first',  # track_id is unique per index_track
    'dummy': 'first'      # dummy is constant 1
})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)