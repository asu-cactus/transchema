import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

# Join on 'track_id' to combine index_track and dummy columns
result = pd.merge(source1, source0, how='inner', on='track_id')

# Select columns as per target schema
result = result[['index_track', 'track_id', 'dummy']]

result.to_csv(target_path, index=False)