import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv", index_col=0)
df0['Dates'] = pd.to_datetime(df0['Dates']).dt.day
grouped = df0.groupby('Dates').size().reset_index(name='Action')
grouped['Dates'] = grouped['Dates'].astype(int)
grouped['Action'] = grouped['Action'].astype(int)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv", index=False)