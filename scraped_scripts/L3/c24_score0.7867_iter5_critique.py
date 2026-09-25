import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_24/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_24/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_24/training_2.csv", index_col=0)

# Join ratings with user info on user_id (inner join to keep only valid ratings)
merged_0_2 = pd.merge(source2, source0[['user_id', 'gender']], on='user_id', how='inner')

# Group by movie_id and gender, aggregate average rating
agg = merged_0_2.groupby(['movie_id', 'gender'], as_index=False)['rating'].mean()

# Join aggregated ratings with movie info on movie_id using right join to keep all movies
result = pd.merge(agg, source1[['movie_id', 'title']], on='movie_id', how='right')

# Pivot to get columns F and M for each title
pivot = result.pivot(index='title', columns='gender', values='rating').reset_index()

pivot.columns.name = None

# Rename columns to match target schema exactly
pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

# Select columns in target schema order
final = pivot[['title', 'F', 'M']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_24/target_multisource_mcts.csv", index=False)