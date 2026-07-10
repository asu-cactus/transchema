import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

# UNION Source4_45_0 and Source4_45_1
union_result = pd.concat([s0, s1], ignore_index=True)

# JOIN union_result with s2 on WarID
join_1 = pd.merge(union_result, s2, on="WarID", how="inner", suffixes=('', '_2'))

# JOIN join_1 with s3 on WarID
join_2 = pd.merge(join_1, s3[['WarID', 'IsInternational']], on="WarID", how="inner")

# Group by WarType and aggregate counts of WarID, WarShortName, IsInternational, IsIntervention
final = join_2.groupby('WarType', as_index=False).agg({
    'WarID': 'count',
    'WarShortName': 'count',
    'IsInternational': 'count',
    'IsIntervention': 'count'
})

# Ensure correct column types
final['WarType'] = final['WarType'].astype(int)
final['WarID'] = final['WarID'].astype(int)
final['WarShortName'] = final['WarShortName'].astype(int)
final['IsInternational'] = final['IsInternational'].astype(int)
final['IsIntervention'] = final['IsIntervention'].astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)