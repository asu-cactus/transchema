import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_3.csv", index_col=0)

# UNION all source tables (concatenate)
unioned = pd.concat([source0, source1, source2, source3], ignore_index=True)

# GROUP BY TrackID to get unique TrackIDs
result = unioned[["TrackID"]].drop_duplicates().sort_values("TrackID").reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts.csv", index=False)