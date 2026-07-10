import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

# LEFT JOIN source1 with source0 on track_id to preserve all rows from source1
joined = pd.merge(source1, source0, on="track_id", how="left")

# Group by index_track and track_id, aggregate dummy by max (dummy is always 1)
result = joined.groupby(['index_track', 'track_id'], as_index=False).agg({'dummy': 'max'})

# Write output with exact target schema and no index
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)