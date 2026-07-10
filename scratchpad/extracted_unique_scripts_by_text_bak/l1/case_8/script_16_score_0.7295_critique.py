import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

# Read sources with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv(source0_path, index_col=0)  # columns: track_id, dummy
df1 = pd.read_csv(source1_path, index_col=0)  # columns: index_track, track_id

# Join on track_id
merged = pd.merge(df1, df0, on="track_id", how="inner")

# Group by index_track and track_id, aggregate dummy by count
grouped = merged.groupby(["index_track", "track_id"], as_index=False).agg(dummy=("dummy", "count"))

# Write output with exact target schema column order
grouped.to_csv(target_path, index=False)