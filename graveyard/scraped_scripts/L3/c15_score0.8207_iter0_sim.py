import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

merged = source2.merge(source1[['user_id', 'gender']], on='user_id', how='inner')

grouped = merged.groupby(['gender', 'movie_id'], as_index=False)['rating'].mean()

grouped_pivot = grouped.pivot(index='movie_id', columns='gender', values='rating').reset_index()

result = grouped_pivot.merge(source0[['movie_id', 'title']], on='movie_id', how='inner')

result = result.rename(columns={'F': 'F', 'M': 'M', 'title': 'title'})

final = result[['title', 'F', 'M']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)