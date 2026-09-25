import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

j1 = pd.merge(s3, s1, on="WarID", suffixes=('_3', '_1'))
j2 = pd.merge(j1, s0, on="WarID", suffixes=('', '_0'))
j3 = pd.merge(j2, s2, on="WarID", suffixes=('', '_2'))

grouped = j3.groupby(
    ['IsInternational', 'WarID', 'WarShortName_3', 'WarType_3', 'IsIntervention'],
    as_index=False
).size()

result = grouped.rename(columns={
    'WarShortName_3': 'WarShortName',
    'WarType_3': 'WarType',
    'size': 'Count'  # size column is not needed, drop it
}).drop(columns=['Count'])

result = result.astype({
    'IsInternational': 'int64',
    'WarID': 'int64',
    'WarShortName': 'int64',
    'WarType': 'int64',
    'IsIntervention': 'int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)