import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_19/training_2.csv", index_col=0)

agg = df1.groupby(['user_id', 'movie_id']).agg({'rating':'mean', 'timestamp':'mean'}).reset_index()

merged_0 = pd.merge(df0, agg, how='inner', left_on='movie_id', right_on='movie_id')

final = pd.merge(merged_0, df2[['user_id', 'age', 'occupation']], how='inner', left_on='user_id', right_on='user_id')

final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_19/target_multisource_mcts.csv", index=False)