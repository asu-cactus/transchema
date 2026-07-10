import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_29/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_29/training_1.csv", index_col=0)

pivot = source1.pivot_table(index='city', columns='type', values=['fare', 'ride_id'], aggfunc={'fare':'mean', 'ride_id':'count'})
pivot.columns = ['Average Fare' if c[0]=='fare' else 'Ride Count' for c in pivot.columns]
pivot = pivot.reset_index()

merged = pd.merge(source0, pivot, on='city')

result = merged.rename(columns={'driver_count':'driver_count', 'type':'type'})
result = result[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_29/target_multisource_mcts.csv", index=False)