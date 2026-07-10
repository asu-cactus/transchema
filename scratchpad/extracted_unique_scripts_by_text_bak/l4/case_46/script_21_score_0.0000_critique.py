import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

# UNION Source4_46_0 and Source4_46_2 (same schema)
union_0_2 = pd.concat([s0, s2], ignore_index=True)

# JOIN Source4_46_3 and Source4_46_1 on WarID to get IsInternational and IsIntervention
join_3_1 = pd.merge(s3, s1[['WarID', 'IsIntervention']], on='WarID', how='inner')

# JOIN union_0_2 and join_3_1 on WarID to combine all columns
final = pd.merge(union_0_2, join_3_1, on='WarID', how='inner')

# Project columns as per target schema:
# Target schema: ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']
# WarShortName in target is integer and matches WarID values in examples, so replace WarShortName with WarID
final = final[['IsInternational', 'WarID', 'WarID', 'WarType_x', 'IsIntervention']]
final.columns = ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']

# Cast columns to correct types
final['IsInternational'] = final['IsInternational'].astype('Int64')
final['WarID'] = final['WarID'].astype('Int64')
final['WarShortName'] = final['WarShortName'].astype('Int64')
final['WarType'] = final['WarType'].astype('Int64')
final['IsIntervention'] = final['IsIntervention'].astype('Int64')

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)