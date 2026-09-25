import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv", index_col=0)
df0['Dates'] = pd.to_datetime(df0['Dates']).dt.floor('D').view('int64') // 10**9 // 86400  # convert to days since epoch as int
result = df0.groupby('Dates', as_index=False).agg({'Action': 'count'})
result['Dates'] = result['Dates'].astype(int)
result['Action'] = result['Action'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv", index=False)