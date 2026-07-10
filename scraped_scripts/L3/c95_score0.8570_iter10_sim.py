import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_2.csv", index_col=0)

merged_1_2 = pd.merge(source1, source2, on='user_id', how='inner')

grouped = merged_1_2.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean().rename(columns={'rating': 'rating_mean'})

joined_0 = pd.merge(grouped, source0[['movie_id', 'title']], on='movie_id', how='inner')

pivoted = joined_0.pivot_table(index=['movie_id', 'title'], columns='sex', values='rating_mean', fill_value=0).reset_index()

pivoted.columns.name = None
pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'})

pivoted['F'] = pivoted.get('F', pd.Series(dtype=float))
pivoted['M'] = pivoted.get('M', pd.Series(dtype=float))

pivoted = pivoted[['movie_id', 'title', 'F', 'M']]

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_95/target_multisource_mcts.csv", index=False)