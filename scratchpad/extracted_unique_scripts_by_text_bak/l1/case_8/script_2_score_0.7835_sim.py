import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby("index_track").agg(
    track_id_count=("track_id", "count"),
    track_id_nunique=("track_id", "nunique")
).reset_index()

# Join aggregated result with source0 on track_id = index_track? 
# But source0 has no index_track, only track_id and dummy.
# The plan says join groupby_result and Source1_8_0 on groupby_result.index_track = Source1_8_0.track_id
# So join agg (index_track, counts) with df0 on agg.index_track == df0.track_id

joined = pd.merge(agg, df0, left_on="index_track", right_on="track_id", how="left")

# Target schema: ['index_track': integer, 'track_id': integer, 'dummy': integer]
# From joined, index_track is from agg, track_id from agg or df0? The target examples show track_id is integer, dummy is 1.
# Use index_track from agg, track_id from agg.track_id_count or from df0.track_id? The target examples show track_id values like 2413161, which matches track_id from source1_8_1.
# The aggregation counts are counts of track_id, not the track_id itself.
# So we should keep index_track and track_id from df1 (or df0?), dummy from df0.

# The aggregation is only used to get group keys, but target schema expects track_id as integer, not counts.
# So better to join df1 and df0 on track_id, then keep index_track, track_id, dummy.

# Let's do a direct join of df1 and df0 on track_id, then keep columns index_track, track_id, dummy.

joined = pd.merge(df1, df0, on="track_id", how="left")

# Ensure columns and types
joined = joined[["index_track", "track_id", "dummy"]]
joined["index_track"] = joined["index_track"].astype(int)
joined["track_id"] = joined["track_id"].astype(int)
joined["dummy"] = joined["dummy"].fillna(0).astype(int)

joined.to_csv(target_path, index=False)