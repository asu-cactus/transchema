import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv", index_col=0)

# Join source1 and source2 on movie_id with left join to keep all movies
merged_1_2 = pd.merge(source1, source2, how='right', on='movie_id')

# Join the above with source0 on user_id with left join to keep all ratings
merged_0_1_2 = pd.merge(merged_1_2, source0, how='left', on='user_id')

# Group by title and gender, aggregate mean rating
grouped = merged_0_1_2.groupby(['title', 'gender'], dropna=False)['rating'].mean().reset_index()

# Pivot gender to columns F and M
pivot = grouped.pivot(index='title', columns='gender', values='rating').reset_index()

# Rename columns to match target schema
pivot = pivot.rename(columns={'F': 'F', 'M': 'M'})

# Ensure columns order
pivot = pivot[['title', 'F', 'M']]

# Fill missing values with 0 (some movies may have no ratings from a gender)
pivot = pivot.fillna(0)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv", index=False)