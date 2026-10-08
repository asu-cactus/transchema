import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

u01 = pd.merge(s0, s1[['WarID','IsIntervention']], on='WarID', how='inner')
u012 = pd.merge(u01, s2[['WarID','WarShortName','WarType']], on='WarID', how='inner', suffixes=('', '_s2'))
u012 = u012.drop(columns=['WarShortName', 'WarType'])
u012 = u012.rename(columns={'WarShortName_s2':'WarShortName', 'WarType_s2':'WarType'})
u0123 = pd.merge(u012, s3[['WarID','IsInternational']], on='WarID', how='inner')

result = u0123[['IsIntervention','WarID','WarShortName','WarType','IsInternational']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)