import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_2.csv", index_col=0)

merged_0_1 = pd.merge(source0, source1, on='user_id', how='inner')
merged_0_1_2 = pd.merge(merged_0_1, source2, on='movie_id', how='inner')

grouped = merged_0_1_2.groupby(['sex', 'occupation', 'release_date', 'movie_id', 'title'], as_index=False)['rating'].mean()

pivot = grouped.pivot_table(index=['movie_id', 'title'], columns='sex', values='rating', aggfunc='mean')

pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

result = pivot.reset_index()

result = result[['movie_id', 'title', 'F', 'M']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_78/target_multisource_mcts.csv", index=False)