import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

agg = df1.groupby(['user_id', 'movie_id'], as_index=False).agg({'rating':'mean', 'timestamp':'mean'})
merged_1 = pd.merge(agg, df2[['user_id', 'age', 'occupation']], on='user_id', how='inner')
final = pd.merge(merged_1, df0[['movie_id', 'title']], on='movie_id', how='inner')

final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)