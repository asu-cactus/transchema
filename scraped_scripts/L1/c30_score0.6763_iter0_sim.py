import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_30/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_30/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length1_30/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df0.groupby('tag', as_index=False).agg({
    'userId': 'first',
    'movieId': 'first',
    'timestamp': 'first'
})

joined1 = pd.merge(grouped, df1, on='movieId', how='inner')

final = pd.merge(joined1, df0, on=['movieId', 'tag'], how='inner', suffixes=('_left', '_right'))

result = final[['movieId', 'title', 'genres', 'userId_right', 'tag', 'timestamp_right']]
result.columns = ['movieId', 'title', 'genres', 'userId', 'tag', 'timestamp']

result = result.astype({
    'movieId': 'int64',
    'title': 'string',
    'genres': 'string',
    'userId': 'int64',
    'tag': 'string',
    'timestamp': 'int64'
})

result.to_csv(output_path, index=False)