import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_50/training_1.csv", index_col=0)

pivot = source0.pivot_table(index='city', columns='date', values='fare', aggfunc=['mean', 'count'])
pivot.columns = ['_'.join(col).strip() for col in pivot.columns.values]
pivot.reset_index(inplace=True)

mean_cols = [col for col in pivot.columns if col.startswith('mean_')]
count_cols = [col for col in pivot.columns if col.startswith('count_')]

pivot['Average Fare'] = pivot[mean_cols].mean(axis=1)
pivot['Ride Count'] = pivot[count_cols].sum(axis=1)

pivot = pivot[['city', 'Average Fare', 'Ride Count']]

result = pd.merge(pivot, source1, on='city', how='inner')

result = result[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_50/target_multisource_mcts.csv", index=False)