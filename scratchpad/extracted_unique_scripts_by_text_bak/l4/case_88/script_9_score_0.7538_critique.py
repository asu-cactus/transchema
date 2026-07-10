import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by TrackID and count occurrences (aggregation)
result = df_all.groupby("TrackID", as_index=False).agg({"TrackID": "count"})

# Rename the count column to something else or drop it, since target schema only has TrackID
# We only need the TrackID column, so select it
result = result[["TrackID"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts.csv", index=False)