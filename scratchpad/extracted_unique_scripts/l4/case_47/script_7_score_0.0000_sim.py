import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

join_01 = pd.merge(source1, source0, on="WarID", suffixes=('_1', '_0'))
join_012 = pd.merge(join_01, source2, on="WarID", suffixes=('', '_2'))
join_all = pd.merge(join_012, source3, on="WarID", suffixes=('', '_3'))

result = join_all[["IsIntervention", "WarID", "WarShortName", "WarType", "IsInternational"]]

result = result.astype({
    "IsIntervention": "Int64",
    "WarID": "Int64",
    "WarShortName": "Int64",
    "WarType": "Int64",
    "IsInternational": "Int64"
}, errors='ignore')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)