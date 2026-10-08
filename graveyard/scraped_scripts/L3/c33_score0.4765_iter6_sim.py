import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_2.csv", index_col=0)

agg = df2.groupby(['user_id', 'movie_id']).agg({'rating':'mean', 'timestamp':'mean'}).reset_index()

merged1 = pd.merge(df1, agg, how='inner', on='user_id')

final = pd.merge(merged1, df0, how='inner', on='movie_id')

final = final.rename(columns={'rating':'rating', 'timestamp':'timestamp', 'title':'title', 'user_id':'user_id', 'movie_id':'movie_id', 'age':'age', 'occupation':'occupation'})

final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_33/target_multisource_mcts.csv", index=False)