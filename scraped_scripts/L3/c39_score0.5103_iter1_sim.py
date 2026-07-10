import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_39/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_39/training_1.csv", index_col=0)

# Source0 is not needed for the target schema, so we only use Source1.

# Unpivot operation is trivial here since Source1 already has movieId and rating columns.
# Just select the needed columns and ensure correct types.

result = df1[['movieId', 'rating']].copy()
result['movieId'] = result['movieId'].astype(int)
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_39/target_multisource_mcts.csv", index=False)