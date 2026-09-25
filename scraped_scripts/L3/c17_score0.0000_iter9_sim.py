import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_2.csv", index_col=0)

union_result = pd.concat([source0, source2], ignore_index=True, sort=False)

merged = union_result.merge(source1[['movie_id', 'title']], on='movie_id', how='inner')

grouped = merged.groupby(['title', 'gender'])['rating'].mean().reset_index()

pivoted = grouped.pivot(index='title', columns='gender', values='rating').reset_index()

pivoted.columns.name = None
pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M', 'title': 'title'})

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_17/target_multisource_mcts.csv", index=False)