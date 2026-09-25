import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

grouped = df0.groupby("track_id").dummy.nunique().reset_index(name="dummy")

merged = pd.merge(grouped, df1, on="track_id", how="inner")

result = merged[["index_track", "track_id", "dummy"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)