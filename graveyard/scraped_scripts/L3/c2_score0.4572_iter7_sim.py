import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_2/training_2.csv", index_col=0)

grouped = df0.groupby(['user_id', 'movie_id'], as_index=False).agg({'rating':'mean', 'timestamp':'mean'})

join1 = pd.merge(grouped, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')

join2 = pd.merge(join1, df1[['movie_id', 'title']], on='movie_id', how='inner')

result = join2[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_2/target_multisource_mcts.csv", index=False)