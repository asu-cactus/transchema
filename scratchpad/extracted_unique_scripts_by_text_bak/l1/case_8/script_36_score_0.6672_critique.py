import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# LEFT JOIN Source1_8_1 (df1) with Source1_8_0 (df0) on 'track_id' to preserve all index_track rows
merged = pd.merge(df1, df0, on="track_id", how="left")

# Select columns in target schema order
result = merged[["index_track", "track_id", "dummy"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)