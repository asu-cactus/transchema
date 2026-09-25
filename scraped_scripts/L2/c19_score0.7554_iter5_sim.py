import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv", index_col=0)
df0['Dates'] = pd.to_datetime(df0['Dates']).dt.day
pivot = df0.pivot_table(index='Dates', columns='Action', aggfunc='size', fill_value=0)
pivot = pivot.reset_index()
pivot['Action'] = pivot.sum(axis=1)
result = pivot[['Dates', 'Action']]
result['Dates'] = result['Dates'].astype(int)
result['Action'] = result['Action'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv", index=False)