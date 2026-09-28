import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_56/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_56/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['PolityName'] = df['PolityName'].astype(str).replace({'nan': None})

for col in ['WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']:
    if col in ['Initiator', 'Outcome']:
        df[col] = df[col].astype(str).str.extract('(\d+)').astype(float).fillna(0).astype(int)
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df = df[['PolityName', 'WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_56/target_multisource_mcts.csv", index=False)