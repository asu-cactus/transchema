import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="track_id", how="inner")

grouped = merged.groupby(["index_track", "track_id"], as_index=False).agg({"dummy": "max"})

result = grouped[["index_track", "track_id", "dummy"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)