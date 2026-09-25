import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df0.groupby('track_id', as_index=False)['dummy'].sum()

merged = pd.merge(df1, grouped, on='track_id', how='inner')

result = merged[['index_track', 'track_id', 'dummy']]

result.to_csv(target_path, index=False)