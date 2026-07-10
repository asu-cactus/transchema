import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_32/training_2.csv", index_col=0)

# PIVOT operations here mean no actual pivot needed, just rename or keep as is.
# Source1 and Source2 have different schemas, so no pivot needed, just keep as is.
# But the plan says PIVOT twice, so we interpret it as no pivot needed, just rename for clarity.

pivot_result_1 = df1.copy()
pivot_result_2 = df2.copy()

# Join pivot_result_1 and pivot_result_2 on movie_id to get title with ratings
join_result_1 = pd.merge(pivot_result_1, pivot_result_2[['movie_id', 'title']], on='movie_id', how='left')

# Join Source0 with the above on user_id to get user info with ratings and title
join_result_2 = pd.merge(df0, join_result_1, on='user_id', how='inner')

# Select and reorder columns to match target schema
result = join_result_2[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Convert data types to match target schema
result['title'] = result['title'].astype(str)
result['user_id'] = result['user_id'].astype(float)
result['movie_id'] = result['movie_id'].astype(int)
result['rating'] = result['rating'].astype(float)
result['timestamp'] = result['timestamp'].astype(float)
result['age'] = result['age'].astype(float)
result['occupation'] = result['occupation'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_32/target_multisource_mcts.csv", index=False)