import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

pivot = df0.groupby(['user_id', 'movie_id']).agg({
    'rating': 'mean',
    'timestamp': 'mean'
}).reset_index()

joined_1 = pd.merge(pivot, df1[['user_id', 'age', 'occupation']], on='user_id', how='left')

final = pd.merge(joined_1, df2[['movie_id', 'title']], on='movie_id', how='left')

final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)