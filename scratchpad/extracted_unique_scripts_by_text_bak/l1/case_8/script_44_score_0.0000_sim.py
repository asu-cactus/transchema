import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

grouped = source1.groupby(['index_track', 'track_id'], as_index=False).agg({'track_id':'count'})
grouped.rename(columns={'track_id':'dummy'}, inplace=True)

result = pd.merge(grouped, source0, how='left', on='track_id')

# The target schema is ['index_track', 'track_id', 'dummy']
# The 'dummy' column from source0 is ignored because target dummy is from count aggregation (constant 1 in examples)
# But the count aggregation is used as dummy, so we keep dummy from grouped count, ignoring source0.dummy

result = result[['index_track', 'track_id', 'dummy']]

result.to_csv(target_path, index=False)