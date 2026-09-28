import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv", index_col=0)

# Join ratings with user info to get gender
joined_0_1 = pd.merge(source1, source0[['user_id', 'gender']], on='user_id', how='inner')

# Join with movie info to get title
joined_all = pd.merge(joined_0_1, source2[['movie_id', 'title']], on='movie_id', how='inner')

# Group by title and gender, aggregate mean rating
grouped = joined_all.groupby(['title', 'gender'], as_index=False)['rating'].mean()

# Pivot gender to columns F and M
pivot = grouped.pivot(index='title', columns='gender', values='rating').reset_index()

# Rename columns to match target schema exactly
pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

# Fill missing values with 0 as per hint 24 (if needed)
pivot['F'] = pivot['F'].fillna(0)
pivot['M'] = pivot['M'].fillna(0)

# Select final columns
final = pivot[['title', 'F', 'M']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv", index=False)