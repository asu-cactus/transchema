import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

join_0_3 = pd.merge(s3, s0, on="WarID", how="inner", suffixes=('_3', '_0'))
join_0_1_3 = pd.merge(join_0_3, s1, on="WarID", how="inner", suffixes=('', '_1'))
join_all = pd.merge(join_0_1_3, s2, on="WarID", how="inner", suffixes=('', '_2'))

# Select columns from appropriate sources to match target schema
# Target schema: ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']
# Use WarShortName and WarType from s3 (suffix _3), IsInternational from s3, IsIntervention from s1

result = join_all[['IsInternational', 'WarID', 'WarShortName_3', 'WarType_3', 'IsIntervention']]

# Rename columns to match target schema exactly
result.columns = ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention']

# Group by IsInternational and WarID to remove duplicates if any
result = result.groupby(['IsInternational', 'WarID'], as_index=False).first()

# Ensure correct dtypes
result = result.astype({
    'IsInternational': 'int64',
    'WarID': 'int64',
    'WarShortName': 'object',  # string type
    'WarType': 'int64',
    'IsIntervention': 'int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)