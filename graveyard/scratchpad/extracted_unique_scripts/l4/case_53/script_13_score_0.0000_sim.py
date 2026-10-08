import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

union_result = pd.concat([s0, s1, s3], ignore_index=True)

merged = pd.merge(
    union_result,
    s2,
    how='inner',
    on=['WarID', 'PolityID', 'StartYear'],
    suffixes=('', '_s2')
)

cols = [
    'PolityName',
    'WarID',
    'PolityID',
    'StartYear',
    'StartMonth',
    'StartDay',
    'EndYear',
    'EndMonth',
    'EndDay',
    'Side',
    'IsInitiator',
    'Outcome',
    'Deaths'
]

df = pd.DataFrame()
df['PolityName'] = merged['PolityName']
df['WarID'] = merged['WarID']
df['PolityID'] = merged['PolityID']
df['StartYear'] = merged['StartYear']
df['StartMonth'] = merged['StartMonth']
df['StartDay'] = merged['StartDay']
df['EndYear'] = merged['EndYear']
df['EndMonth'] = merged['EndMonth']
df['EndDay'] = merged['EndDay']
df['Side'] = merged['Side']
df['IsInitiator'] = merged['IsInitiator']
df['Outcome'] = merged['Outcome']
df['Deaths'] = merged['Deaths']

df['PolityName'] = df['PolityName'].astype(str)
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['PolityID'] = pd.to_numeric(df['PolityID'], errors='coerce').astype('Int64')
df['StartYear'] = pd.to_numeric(df['StartYear'], errors='coerce').astype('Int64')
df['StartMonth'] = pd.to_numeric(df['StartMonth'], errors='coerce').astype('Int64')
df['StartDay'] = pd.to_numeric(df['StartDay'], errors='coerce').astype('Int64')
df['EndYear'] = pd.to_numeric(df['EndYear'], errors='coerce').astype('Int64')
df['EndMonth'] = pd.to_numeric(df['EndMonth'], errors='coerce').astype('Int64')
df['EndDay'] = pd.to_numeric(df['EndDay'], errors='coerce').astype('Int64')
df['Side'] = pd.to_numeric(df['Side'], errors='coerce').astype('Int64')
df['IsInitiator'] = pd.to_numeric(df['IsInitiator'], errors='coerce').astype('Int64')
df['Outcome'] = pd.to_numeric(df['Outcome'], errors='coerce').astype('Int64')
df['Deaths'] = pd.to_numeric(df['Deaths'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)