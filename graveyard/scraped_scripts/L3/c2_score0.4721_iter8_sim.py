import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)

agg = df0.groupby(['user_id', 'movie_id']).agg(
    rating=('rating', 'count'),
    timestamp_min=('timestamp', 'min'),
    timestamp_max=('timestamp', 'max')
).reset_index()

join1 = pd.merge(agg, df1[['movie_id', 'title']], on='movie_id', how='inner')

join2 = pd.merge(join1, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

join2['timestamp'] = (join2['timestamp_min'] + join2['timestamp_max']) / 2

result = join2[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

result.to_csv(target_path, index=False)