import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_94/training_2.csv", index_col=0)

ratings = pd.merge(source1, source2[['user_id', 'sex']], on='user_id')
ratings['F'] = ratings.apply(lambda row: row['rating'] if row['sex'] == 'F' else pd.NA, axis=1)
ratings['M'] = ratings.apply(lambda row: row['rating'] if row['sex'] == 'M' else pd.NA, axis=1)

agg = ratings.groupby('movie_id').agg({'F': 'mean', 'M': 'mean'}).reset_index()

merged = pd.merge(source0[['movie_id', 'title']], agg, on='movie_id', how='left')

merged = merged[['movie_id', 'title', 'F', 'M']]
merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_94/target_multisource_mcts.csv", index=False)