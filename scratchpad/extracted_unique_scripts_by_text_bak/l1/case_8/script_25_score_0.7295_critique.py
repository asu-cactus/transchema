import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# Join Source1_8_1 and Source1_8_0 on 'track_id' with inner join
result = pd.merge(df1, df0, on='track_id', how='inner')

# Select and reorder columns as per target schema
final = result[['index_track', 'track_id', 'dummy']].copy()

# Convert to appropriate integer types with nullable Int64 dtype
final = final.astype({'index_track': 'Int64', 'track_id': 'Int64', 'dummy': 'Int64'})

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)