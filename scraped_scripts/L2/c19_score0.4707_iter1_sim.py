import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv", index_col=0)
df = pd.concat([df0], ignore_index=True)
df = df[['Dates', 'Action']]
df['Dates'] = pd.to_datetime(df['Dates']).dt.day
df['Action'] = df['Action'].astype('category').cat.codes
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv", index=False)