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

df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce')
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce')
df['PolityName'] = pd.to_numeric(df['PolityName'], errors='coerce')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce')

agg_df = df.groupby('Initiator', dropna=False).agg({
    'StartYear': 'min',
    'EndYear': 'max',
    'Deaths': 'sum',
    'WarID': 'min',
    'PolityName': 'min',
    'StartMonth': 'min',
    'StartDay': 'min',
    'EndMonth': 'min',
    'EndDay': 'min',
    'Outcome': 'min'
}).reset_index()

agg_df = agg_df.rename(columns={
    'Initiator': 'Initiator',
    'WarID': 'WarID',
    'PolityName': 'PolityName',
    'StartYear': 'StartYear',
    'StartMonth': 'StartMonth',
    'StartDay': 'StartDay',
    'EndYear': 'EndYear',
    'EndMonth': 'EndMonth',
    'EndDay': 'EndDay',
    'Outcome': 'Outcome',
    'Deaths': 'Deaths'
})

agg_df = agg_df.astype({
    'Initiator': 'string',
    'WarID': 'Int64',
    'PolityName': 'Int64',
    'StartYear': 'Int64',
    'StartMonth': 'Int64',
    'StartDay': 'Int64',
    'EndYear': 'Int64',
    'EndMonth': 'Int64',
    'EndDay': 'Int64',
    'Outcome': 'Int64',
    'Deaths': 'Int64'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_79/target_multisource_mcts.csv", index=False)