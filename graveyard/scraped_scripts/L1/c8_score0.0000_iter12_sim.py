import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length1_8/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_8/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

agg = df1.groupby(['index_track', 'track_id'], as_index=False).agg({'index_track': ['min', 'max']})
agg.columns = ['index_track', 'track_id', 'min_index_track', 'max_index_track']

joined = pd.merge(agg, df0, how='left', left_on='track_id', right_on='track_id')

result = joined[['index_track', 'track_id', 'dummy']]

result.to_csv(target_path, index=False)