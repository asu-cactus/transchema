import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_6/training_2.csv", index_col=0)

# The partial plan says UNION of Source3_6_0, Source3_6_1, Source3_6_2 then UNPIVOT
# But Source0 schema is unrelated to target, so UNION is not possible across all three.
# Instead, we must join Source2 (ratings) with Source1 (movie titles) on movie id.
# Source0 is unrelated to target schema and can be ignored.

# Join Source2 and Source1 on 'movie id' to get movie title and rating
merged = pd.merge(source2, source1[['movie id', 'movie title']], on='movie id', how='inner')

# Select only needed columns and convert rating to float
result = merged[['movie title', 'rating']].copy()
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_6/target_multisource_mcts.csv", index=False)