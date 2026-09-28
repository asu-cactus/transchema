import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_88/training_3.csv", index_col=0)

join_01 = pd.merge(df0[['TrackID']], df1[['TrackID']], left_on='TrackID', right_on='TrackID', how='inner', suffixes=('_0', '_1'))
join_012 = pd.merge(join_01[['TrackID']], df2[['TrackID']], left_on='TrackID', right_on='TrackID', how='inner')
join_0123 = pd.merge(join_012[['TrackID']], df3[['TrackID']], left_on='TrackID', right_on='TrackID', how='inner')

result = join_0123.groupby('TrackID', as_index=False).size().drop(columns='size', errors='ignore')
result = result[['TrackID']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_88/target_multisource_mcts.csv", index=False)