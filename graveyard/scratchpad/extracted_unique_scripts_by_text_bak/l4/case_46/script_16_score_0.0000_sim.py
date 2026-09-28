import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_46/training_3.csv", index_col=0)

join_0_3 = pd.merge(s3, s0, on="WarID", suffixes=('_3', '_0'))
join_0_1_3 = pd.merge(join_0_3, s1, on="WarID", suffixes=('', '_1'))
join_all = pd.merge(join_0_1_3, s2, on="WarID", suffixes=('', '_2'))

grouped = join_all.groupby(
    ['IsInternational', 'WarID', 'WarShortName', 'WarType', 'IsIntervention'],
    as_index=False
).size()

result = grouped.drop(columns='size')

result = result.astype({
    'IsInternational': 'int64',
    'WarID': 'int64',
    'WarShortName': 'int64',
    'WarType': 'int64',
    'IsIntervention': 'int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_46/target_multisource_mcts.csv", index=False)