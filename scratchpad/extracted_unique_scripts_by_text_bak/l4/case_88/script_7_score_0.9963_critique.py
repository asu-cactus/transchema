import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY TrackID to get unique TrackIDs
result = df_all[['TrackID']].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts.csv", index=False)