import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv", index_col=0)

source1['time'] = pd.to_datetime(source1['time'], errors='coerce').dt.hour
source1[['bet', 'win']] = source1[['bet', 'win']].fillna(0).astype(int)

merged = pd.merge(source1, source0, on='user_id', how='inner')

merged['email'] = merged['email'].astype(str).str.len()
merged['geo'] = merged['geo'].astype(str).str.len()

result = merged[['user_id', 'time', 'bet', 'win', 'email', 'geo']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv", index=False)