import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

u0_2 = pd.concat([s0, s2], ignore_index=True)
u1_3 = pd.concat([s1, s3], ignore_index=True)

merged = pd.merge(u0_2, u1_3, on="WarID", how="inner", suffixes=('_left', '_right'))

result = pd.DataFrame()
result['WarID'] = merged['WarID']
result['WarShortName'] = merged['WarShortName_left']
result['WarType'] = merged['WarType_left']
result['IsInternational'] = merged['IsInternational']
result['IsIntervention'] = merged['IsIntervention']

result = result.astype({
    'IsInternational': 'Int64',
    'WarID': 'Int64',
    'WarShortName': 'Int64',
    'WarType': 'Int64',
    'IsIntervention': 'Int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)