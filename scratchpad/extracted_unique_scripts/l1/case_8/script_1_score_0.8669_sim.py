import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df1.groupby(['index_track', 'track_id'], as_index=False).size().rename(columns={'size': 'count_index_track'})

merged = pd.merge(grouped, df0, how='left', on='track_id')

result = merged[['index_track', 'track_id']].copy()
result['dummy'] = 1

result.to_csv(target_path, index=False)