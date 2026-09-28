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

df['PolityName'] = df['PolityName'].astype(str).replace({'nan': None, 'NaN': None, 'None': None})
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').fillna(0).astype(int)
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').fillna(0).astype(int)
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').fillna(0).astype(int)
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').fillna(0).astype(int)

# Initiator column: source has strings like 'A', 'B', target expects integer
# Map unique initiator strings to integers preserving order of appearance
initiator_map = {v: i+1 for i, v in enumerate(pd.Series(df['Initiator'].dropna().unique()))}
df['Initiator'] = df['Initiator'].map(initiator_map).astype('Int64')

df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').fillna(0).astype(int)

df = df[['PolityName', 'WarID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Initiator', 'Outcome', 'Deaths']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_56/target_multisource_mcts.csv", index=False)