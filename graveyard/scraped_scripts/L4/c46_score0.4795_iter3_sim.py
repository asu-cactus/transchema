import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

source3_renamed = source3.rename(columns={"IsInternational": "IsInternational"})
source1_renamed = source1.rename(columns={"IsIntervention": "IsIntervention"})

merged_01 = pd.merge(source3_renamed, source1_renamed, on="WarID", how="outer", suffixes=('_3', '_1'))

merged_01['IsInternational'] = merged_01['IsInternational'].fillna(0).astype(int)
merged_01['IsIntervention'] = merged_01['IsIntervention'].fillna(0).astype(int)

merged_01['WarShortName'] = merged_01['WarShortName_3'].combine_first(merged_01['WarShortName_1'])
merged_01['WarType'] = merged_01['WarType_3'].combine_first(merged_01['WarType_1'])

union_01 = merged_01[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

source0['IsInternational'] = 0
source0['IsIntervention'] = 0
source2['IsInternational'] = 0
source2['IsIntervention'] = 0

df0 = source0[['IsInternational', 'WarID', 'WarShortName', 'WarType']]
df0['IsIntervention'] = 0

df2 = source2[['IsInternational', 'WarID', 'WarShortName', 'WarType']]
df2['IsIntervention'] = 0

final_df = pd.concat([union_01, df0, df2], ignore_index=True)

final_df = final_df[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

final_df['IsInternational'] = final_df['IsInternational'].astype(int)
final_df['WarID'] = final_df['WarID'].astype(int)
final_df['WarShortName'] = final_df['WarShortName'].astype(str)
final_df['WarType'] = final_df['WarType'].astype(int)
final_df['IsIntervention'] = final_df['IsIntervention'].astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)