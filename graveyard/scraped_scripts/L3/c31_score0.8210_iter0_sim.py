import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_2.csv", index_col=0)

merged = source2.merge(source1[['user_id', 'gender']], on='user_id', how='inner')
merged = merged.merge(source0[['movie_id', 'title']], on='movie_id', how='inner')

grouped = merged.groupby(['title', 'gender'], as_index=False)['rating'].mean()

pivot = grouped.pivot(index='title', columns='gender', values='rating').reset_index()
pivot.columns.name = None
pivot = pivot.rename(columns={'F': 'F', 'M': 'M', 'title': 'title'})

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_31/target_multisource_mcts.csv", index=False)