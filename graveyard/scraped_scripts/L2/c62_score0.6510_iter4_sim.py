import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_1.csv", index_col=0)

pivot_df0 = df0.groupby('city').size().reset_index(name='driver_count')

result = pd.concat([pivot_df0, df1[['city', 'driver_count']]], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_62/target_multisource_mcts.csv", index=False)