import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_1.csv", index_col=0)

groupby_result = df1.groupby('city', as_index=False).agg({'ride_id':'first'})

joined = pd.merge(df0, groupby_result, how='inner', left_on='city', right_on='city')

result = joined[['type', 'ride_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_84/target_multisource_mcts.csv", index=False)