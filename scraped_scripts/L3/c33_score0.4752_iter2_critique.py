import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_2.csv", index_col=0)

merged = df2.merge(df0[['movie_id', 'title']], on='movie_id', how='inner')
merged = merged.merge(df1[['user_id', 'age', 'occupation']], on='user_id', how='inner')

result = merged.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_33/target_multisource_mcts.csv", index=False)