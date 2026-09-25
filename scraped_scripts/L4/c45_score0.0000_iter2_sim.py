import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_result = pd.concat([s0, s1], ignore_index=True)

join_result = pd.merge(s2, s3, on="WarID", how="inner", suffixes=('_2', '_3'))

final = pd.merge(union_result, join_result, on="WarID", how="inner")

final = final[['WarType_2', 'WarID', 'WarShortName_2', 'IsInternational', 'IsIntervention']]

final.columns = ['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']

final['WarType'] = final['WarType'].astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(int)
final['IsInternational'] = final['IsInternational'].astype(int)
final['IsIntervention'] = final['IsIntervention'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)