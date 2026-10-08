import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby("index_track").agg(track_id_min=("track_id", "min"), track_id_max=("track_id", "max")).reset_index()

agg["track_id"] = agg["track_id_min"]
agg = agg.drop(columns=["track_id_min", "track_id_max"])

merged = pd.merge(agg, df0, how="left", on="track_id")

result = merged[["index_track", "track_id", "dummy"]]

result.to_csv(target_path, index=False)