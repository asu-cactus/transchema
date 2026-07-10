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

group_cols = ['Initiator', 'WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']

df_grouped = df.groupby(group_cols, dropna=False, as_index=False).size()

df_grouped = df_grouped[group_cols]

for col in ['WarID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Outcome', 'Deaths']:
    df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').astype('Int64')

df_grouped['Initiator'] = df_grouped['Initiator'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)