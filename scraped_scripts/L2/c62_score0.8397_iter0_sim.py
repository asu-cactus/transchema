import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_62/training_1.csv", index_col=0)

groupby_result = df0.groupby('city').size().reset_index(name='ride_count')

joined = pd.merge(df1, groupby_result, how='inner', left_on='city', right_on='city')

result = joined[['city', 'driver_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_62/target_multisource_mcts.csv", index=False)