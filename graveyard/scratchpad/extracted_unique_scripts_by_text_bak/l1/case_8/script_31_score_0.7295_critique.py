import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)  # columns: track_id, dummy
df1 = pd.read_csv(source1_path, index_col=0)  # columns: index_track, track_id

# Join on track_id
joined = pd.merge(df1, df0, on="track_id", how="inner")

# Select and reorder columns as per target schema
joined = joined[["index_track", "track_id", "dummy"]]

# Ensure correct types
joined["index_track"] = joined["index_track"].astype(int)
joined["track_id"] = joined["track_id"].astype(int)
joined["dummy"] = joined["dummy"].astype(int)

joined.to_csv(target_path, index=False)