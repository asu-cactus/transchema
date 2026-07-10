import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

# Join ratings with user info to get gender
merged_21 = pd.merge(source2, source1[['user_id', 'gender']], on='user_id', how='inner')

# Join with movies to get title
merged_all = pd.merge(merged_21, source0[['movie_id', 'title']], on='movie_id', how='inner')

# Group by title and gender, aggregate mean rating
grouped = merged_all.groupby(['title', 'gender'], as_index=False)['rating'].mean()

# Pivot gender to columns F and M
pivoted = grouped.pivot(index='title', columns='gender', values='rating').reset_index()

# Ensure columns are exactly as target schema
pivoted = pivoted.rename(columns={'F': 'F', 'M': 'M'})

# Left join with all titles to keep all movies (including those without ratings)
result = pd.merge(source0[['title']], pivoted, on='title', how='left')

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)