import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv", index_col=0)

merged_0_1 = pd.merge(source1, source0[['user_id', 'gender']], on='user_id', how='inner')

grouped = merged_0_1.groupby(['movie_id', 'gender'], as_index=False)['rating'].mean()

pivot = grouped.pivot(index='movie_id', columns='gender', values='rating').reset_index()

pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

result = pd.merge(pivot, source2[['movie_id', 'title']], on='movie_id', how='inner')

final = result[['title', 'F', 'M']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv", index=False)