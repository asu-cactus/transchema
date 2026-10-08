import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_result = pd.concat([s0, s1], ignore_index=True)

join_result = pd.merge(s2, s3, on="WarID", how="inner", suffixes=('_2', '_3'))

final = pd.merge(union_result, join_result[['WarID', 'IsInternational', 'IsIntervention']], on="WarID", how="inner")

final = final[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

final['WarType'] = final['WarType'].astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(str)
final['IsInternational'] = final['IsInternational'].fillna(0).astype(int)
final['IsIntervention'] = final['IsIntervention'].fillna(0).astype(int)

final['WarShortName'] = final['WarShortName'].apply(lambda x: int(x) if str(x).isdigit() else 0)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)