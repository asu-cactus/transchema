import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

grouped = df.groupby('Initiator', dropna=False).agg({
    'WarID': 'sum',
    'PolityName': 'sum',
    'StartYear': 'sum',
    'StartMonth': 'sum',
    'StartDay': 'sum',
    'EndYear': 'sum',
    'EndMonth': 'sum',
    'EndDay': 'sum',
    'Outcome': 'sum',
    'Deaths': 'sum'
}).reset_index()

cols = ['Initiator', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']
grouped = grouped[cols]

for c in ['WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']:
    grouped[c] = pd.to_numeric(grouped[c], errors='coerce').astype('Int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)