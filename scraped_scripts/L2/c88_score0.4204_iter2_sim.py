import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

df1 = df1[['city', 'fare', 'ride_id']]
df1['fare'] = df1['fare'].astype(float)
df1['ride_id'] = pd.to_numeric(df1['ride_id'], errors='coerce').astype('Int64')

df1.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)