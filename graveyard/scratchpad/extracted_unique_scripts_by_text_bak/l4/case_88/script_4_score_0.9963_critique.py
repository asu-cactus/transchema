import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_3.csv", index_col=0)

# Concatenate all TrackID columns from all sources (UNION)
union_df = pd.concat([df0[['TrackID']], df1[['TrackID']], df2[['TrackID']], df3[['TrackID']]], ignore_index=True)

# Group by TrackID to get unique TrackIDs
result = union_df.groupby('TrackID', as_index=False).size().drop(columns='size', errors='ignore')
result = result[['TrackID']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts.csv", index=False)