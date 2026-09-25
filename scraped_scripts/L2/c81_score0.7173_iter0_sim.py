import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)

grouped = df0.groupby('city', as_index=False).size().rename(columns={'size': 'ride_count'})
# The partial plan says GROUP_BY city, but target needs driver_count, which is from df1.
# So we join df1 with grouped on city to keep driver_count from df1.

joined = pd.merge(df1[['city', 'driver_count']], grouped[['city']], on='city', how='inner')

result = joined[['city', 'driver_count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_81/target_multisource_mcts.csv", index=False)