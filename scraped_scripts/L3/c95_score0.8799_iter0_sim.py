import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_2.csv", index_col=0)

merged_1_2 = pd.merge(source1, source2[['user_id', 'sex']], on='user_id', how='inner')

grouped = merged_1_2.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean()

pivoted = grouped.pivot(index='movie_id', columns='sex', values='rating').reset_index()
pivoted.columns.name = None
pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'})

final = pd.merge(source0[['movie_id', 'title']], pivoted, on='movie_id', how='left')

final = final[['movie_id', 'title', 'F', 'M']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_95/target_multisource_mcts.csv", index=False)