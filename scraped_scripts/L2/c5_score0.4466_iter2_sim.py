import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_5/training_1.csv", index_col=0)
df1 = df1[['city', 'ride_id']]
df1['ride_id'] = df1['ride_id'].astype('Int64')

df1.to_csv("autopipeline-benchmarks/github-pipelines/length2_5/target_multisource_mcts.csv", index=False)