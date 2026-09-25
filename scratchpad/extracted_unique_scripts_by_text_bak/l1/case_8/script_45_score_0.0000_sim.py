import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

grouped = df1.groupby("index_track").agg(
    count_track_id=("track_id", "count"),
    count_distinct_track_id=("track_id", pd.Series.nunique)
).reset_index()

merged = pd.merge(grouped, df0, left_on="count_track_id", right_on="track_id", how="inner")

result = merged[["index_track", "track_id", "dummy"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)