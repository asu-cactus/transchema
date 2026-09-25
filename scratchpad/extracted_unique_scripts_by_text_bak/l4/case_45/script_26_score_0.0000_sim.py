import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

join_01 = pd.merge(s0, s1, on="WarID", suffixes=('_0', '_1'))
join_012 = pd.merge(join_01, s2, on="WarID", how="inner", suffixes=('', '_2'))
join_0123 = pd.merge(join_012, s3, on="WarID", how="inner", suffixes=('', '_3'))

df = join_0123.copy()

df['WarType'] = df['WarType_0']
df['WarShortName'] = df['WarShortName_0']
df['IsIntervention'] = df['IsIntervention']
df['IsInternational'] = df['IsInternational']
df['WarID'] = df['WarID']

result = df[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

result['WarType'] = result['WarType'].astype('Int64')
result['WarID'] = result['WarID'].astype('Int64')
result['WarShortName'] = result['WarShortName'].astype(str).apply(lambda x: hash(x) % (10**9))
result['IsInternational'] = result['IsInternational'].astype('Int64')
result['IsIntervention'] = result['IsIntervention'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)