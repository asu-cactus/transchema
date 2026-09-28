import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_30/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_30/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_30/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df_merged = pd.merge(df0, df1, how='inner', on='movieId')

df_result = df_merged[['movieId', 'title', 'genres', 'userId', 'tag', 'timestamp']]

df_result.to_csv(target_path, index=False)