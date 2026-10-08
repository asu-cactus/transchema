import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)

pivoted = df0.groupby('city').size().reset_index(name='driver_count')

result = pd.concat([pivoted, df1[['city', 'driver_count']]], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_81/target_multisource_mcts.csv", index=False)