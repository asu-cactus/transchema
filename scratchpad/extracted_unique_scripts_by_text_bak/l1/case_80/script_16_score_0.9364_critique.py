import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)

# No union needed since only one source table, but to follow the plan, we treat it as union of one table
union_df = df0.copy()

# Group by movieId and aggregate mean rating
result = union_df.groupby('movieId', as_index=False)['rating'].mean()

# Ensure correct types
result['movieId'] = result['movieId'].astype(int)
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)