import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_22/training_0.csv", index_col=0)

df_union = df0[['city', 'ride_id']].copy()
df_union['ride_id'] = df_union['ride_id'].astype('Int64')

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length2_22/target_multisource_mcts.csv", index=False)