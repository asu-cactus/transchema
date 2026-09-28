import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

join_2_0 = pd.merge(s2, s0[['WarID','PolityID','PolityName']], on=['WarID','PolityID'], how='left')

union_013 = pd.concat([s0, s1, s3], ignore_index=True, sort=False)

final = pd.merge(union_013, join_2_0.drop(columns=['PolityName']), on=['WarID','PolityID'], how='left', suffixes=('', '_dup'))

final = final[['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']]

final['PolityName'] = final['PolityName'].astype(str)
final['WarID'] = final['WarID'].astype('Int64')
final['PolityID'] = final['PolityID'].astype('Int64')
final['StartYear'] = final['StartYear'].astype('Int64')
final['StartMonth'] = final['StartMonth'].fillna(0).astype('Int64')
final['StartDay'] = final['StartDay'].fillna(0).astype('Int64')
final['EndYear'] = final['EndYear'].astype('Int64')
final['EndMonth'] = final['EndMonth'].fillna(0).astype('Int64')
final['EndDay'] = final['EndDay'].fillna(0).astype('Int64')
final['Side'] = final['Side'].map({'A':1, 'B':2}).fillna(0).astype('Int64')
final['IsInitiator'] = final['IsInitiator'].astype('Int64')
final['Outcome'] = final['Outcome'].astype('Int64')
final['Deaths'] = final['Deaths'].fillna(0).astype('Int64')

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)