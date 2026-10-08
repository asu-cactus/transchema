import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

j0 = pd.merge(s3, s0, on="WarID", suffixes=('_3', '_0'))
j1 = pd.merge(j0, s1, on="WarID", how="left", suffixes=('', '_1'))

# s2 has no IsInternational or IsIntervention, so add those columns with default 0 to match schema for union
s2 = s2.copy()
s2['IsInternational'] = 0
s2['IsIntervention'] = 0

# Select columns to match target schema before union
j1_sel = j1[['IsInternational', 'WarID', 'WarShortName_0', 'WarType_0', 'IsIntervention']]
j1_sel = j1_sel.rename(columns={'WarShortName_0': 'WarShortName', 'WarType_0': 'WarType'})

s2_sel = s2[['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']]

union_df = pd.concat([j1_sel, s2_sel], ignore_index=True)

result = union_df.groupby(['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention'], as_index=False).size()

# The groupby with size() returns a 'size' column, but target schema does not have count column, so drop it
result = result.drop(columns=['size'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)