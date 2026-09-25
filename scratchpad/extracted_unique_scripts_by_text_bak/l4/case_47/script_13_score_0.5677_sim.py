import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

s0_2 = pd.concat([s0, s2], ignore_index=True, sort=False)

s0_2_1 = pd.concat([s0_2, s1], ignore_index=True, sort=False)

all_sources = pd.concat([s0_2_1, s3], ignore_index=True, sort=False)

all_sources['IsIntervention'] = all_sources['IsIntervention'].fillna(0).astype(int)
all_sources['IsInternational'] = all_sources['IsInternational'].fillna(0).astype(int)

all_sources['WarShortName'] = pd.to_numeric(all_sources['WarShortName'], errors='coerce')
all_sources['WarShortName'] = all_sources['WarShortName'].fillna(all_sources['WarID']).astype(int)

all_sources['WarID'] = all_sources['WarID'].astype(int)
all_sources['WarType'] = all_sources['WarType'].astype(int)

target = all_sources[['IsIntervention', 'WarID', 'WarShortName', 'WarType', 'IsInternational']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)