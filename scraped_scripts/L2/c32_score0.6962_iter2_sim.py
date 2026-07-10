import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_32/training_1.csv", index_col=0)

df0_grouped = df0.groupby('city', as_index=False)['ride_id'].max()

df_target = df0_grouped[['city', 'ride_id']]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length2_32/target_multisource_mcts.csv", index=False)