import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

agg = s1.groupby('WarType').agg(
    WarID=('WarID', 'count'),
    IsIntervention=('IsIntervention', 'mean'),
    WarShortName=('WarShortName', pd.Series.nunique)
).reset_index()

agg['IsIntervention'] = agg['IsIntervention'].round().astype('Int64')
agg['WarShortName'] = agg['WarShortName'].astype('Int64')
agg['WarID'] = agg['WarID'].astype('Int64')

join1 = pd.merge(agg, s3[['WarType', 'IsInternational']], on='WarType', how='left')
join2 = pd.merge(join1, s0[['WarType']], on='WarType', how='left')

join2['IsInternational'] = join2['IsInternational'].fillna(0).astype('Int64')
join2['WarType'] = join2['WarType'].astype('Int64')

result = join2[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)