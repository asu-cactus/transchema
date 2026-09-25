import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_2.csv", index_col=0)

# Join Source1 and Source2 on user_id to get sex info with ratings
merged_1_2 = pd.merge(source1, source2[['user_id', 'sex']], on='user_id', how='inner')

# Group by movie_id and sex, aggregate mean rating
grouped = merged_1_2.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean()

# Pivot to get columns F and M
pivot = grouped.pivot(index='movie_id', columns='sex', values='rating')

# Rename columns to match target schema exactly
pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

# Join with source0 on movie_id using inner join to keep only movies with ratings
result = pd.merge(source0[['movie_id', 'title']], pivot, on='movie_id', how='inner')

# Group by movie_id and title to ensure uniqueness and aggregate mean for F and M (in case of duplicates)
result = result.groupby(['movie_id', 'title'], as_index=False).agg({'F': 'mean', 'M': 'mean'})

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_95/target_multisource_mcts.csv", index=False)