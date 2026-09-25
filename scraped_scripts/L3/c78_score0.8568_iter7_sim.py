import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_2.csv", index_col=0)

merged_0 = pd.merge(source0, source1, on='user_id', how='inner')

grouped = merged_0.groupby(['sex', 'movie_id'], as_index=False)['rating'].mean()
grouped.rename(columns={'rating': 'rating_agg'}, inplace=True)

merged_1 = pd.merge(grouped, source2[['movie_id', 'title']], on='movie_id', how='inner')

pivot = merged_1.pivot_table(index=['movie_id', 'title'], columns='sex', values='rating_agg', fill_value=0).reset_index()

pivot.columns.name = None

pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_78/target_multisource_mcts.csv", index=False)