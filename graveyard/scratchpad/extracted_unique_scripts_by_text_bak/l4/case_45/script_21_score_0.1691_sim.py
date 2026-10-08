import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

all_warids = pd.concat([s0[['WarID']], s1[['WarID']], s2[['WarID']], s3[['WarID']]]).drop_duplicates()

pivoted = pd.concat([s0, s1, s2[['WarID', 'WarType']], s3[['WarID', 'WarType']]]).drop_duplicates(subset=['WarID'])
pivoted = pivoted[['WarID', 'WarType']].drop_duplicates()

grouped = pivoted.groupby('WarType', as_index=False).first()

df = all_warids.copy()

df = df.merge(pivoted, on='WarID', how='left')

df = df.merge(s2[['WarID', 'IsIntervention']], on='WarID', how='left')
df = df.merge(s3[['WarID', 'IsInternational']], on='WarID', how='left')

df = df.merge(s0[['WarID', 'WarShortName']], on='WarID', how='left')
df = df.merge(s1[['WarID', 'WarShortName']], on='WarID', how='left', suffixes=('', '_s1'))

df['WarShortName'] = df['WarShortName'].combine_first(df['WarShortName_s1'])
df.drop(columns=['WarShortName_s1'], inplace=True)

df = df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

df['WarType'] = pd.to_numeric(df['WarType'], errors='coerce').astype('Int64')
df['WarID'] = pd.to_numeric(df['WarID'], errors='coerce').astype('Int64')
df['WarShortName'] = pd.to_numeric(df['WarShortName'], errors='coerce').astype('Int64', errors='ignore') if df['WarShortName'].dtype != 'int64' else df['WarShortName']
df['IsInternational'] = pd.to_numeric(df['IsInternational'], errors='coerce').fillna(0).astype('Int64')
df['IsIntervention'] = pd.to_numeric(df['IsIntervention'], errors='coerce').fillna(0).astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)