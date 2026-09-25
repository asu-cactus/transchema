import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_result = pd.concat([s0, s1], ignore_index=True)

join_result_1 = pd.merge(union_result, s2[['WarID', 'IsIntervention']], on='WarID', how='left')

join_result_2 = pd.merge(join_result_1, s3[['WarID', 'IsInternational']], on='WarID', how='left')

join_result_2['WarType'] = join_result_2['WarType'].astype('Int64')
join_result_2['WarID'] = join_result_2['WarID'].astype('Int64')
join_result_2['WarShortName'] = join_result_2['WarShortName'].astype('Int64', errors='ignore')
join_result_2['IsInternational'] = join_result_2['IsInternational'].fillna(0).astype('Int64')
join_result_2['IsIntervention'] = join_result_2['IsIntervention'].fillna(0).astype('Int64')

# WarShortName in target schema is integer, but source columns are strings. 
# The target examples show WarShortName as integer values equal to WarID.
# So convert WarShortName to WarID integer values.
join_result_2['WarShortName'] = join_result_2['WarID']

target = join_result_2[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)