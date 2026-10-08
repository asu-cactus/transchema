import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv", index_col=0)
df0['Dates'] = pd.to_datetime(df0['Dates'])
min_date = df0['Dates'].min()
df0['Dates'] = (df0['Dates'] - min_date).dt.days.astype(int)
agg = df0.groupby('Dates', as_index=False).agg(Action=('Action', 'count'))
agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv", index=False)