import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df0.groupby(['userId', 'movieId'], as_index=False).agg({'rating':'mean'})
grouped.rename(columns={'rating':'rating'}, inplace=True)

merged = pd.merge(grouped, df1, on='movieId', how='inner')

result = merged[['movieId', 'title', 'genres', 'userId', 'rating']]

result.to_csv(target_path, index=False)