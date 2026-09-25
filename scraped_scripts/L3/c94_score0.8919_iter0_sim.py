import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_2.csv", index_col=0)

ratings_users = pd.merge(source1, source2[['user_id', 'sex']], on='user_id', how='inner')

grouped = ratings_users.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean().rename(columns={'rating':'rating_mean'})

merged = pd.merge(source0[['movie_id', 'title']], grouped, on='movie_id', how='inner')

pivoted = merged.pivot(index=['movie_id', 'title'], columns='sex', values='rating_mean').reset_index()

pivoted.columns.name = None

pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'})

pivoted = pivoted.astype({'movie_id': int})

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_94/target_multisource_mcts.csv", index=False)