import pandas as pd

Source4_83_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
Source4_83_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

grouped_Source4_83_0 = Source4_83_0.groupby('city').agg(
    driver_count=('ride_id', 'count'),
    average_fare=('fare', 'mean')
).reset_index()

result = pd.merge(Source4_83_1, grouped_Source4_83_0, on='city', how='inner')

result = result[['city', 'driver_count', 'type', 'average_fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)