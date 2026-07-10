import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="track_id", how="left")

result = merged[["index_track", "track_id", "dummy"]].copy()

result["index_track"] = result["index_track"].astype(int)
result["track_id"] = result["track_id"].astype(int)
result["dummy"] = result["dummy"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv", index=False)