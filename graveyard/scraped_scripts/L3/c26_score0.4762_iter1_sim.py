import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_26/training_1.csv", index_col=0)

pivot = source0.pivot_table(index='movie_id', columns='user_id', values='rating', aggfunc='first').reset_index()

merged = pd.merge(pivot, source1[['movie_id', 'title']], on='movie_id', how='left')

result = merged[['title']].copy()
if 0 in merged.columns:
    result[0] = merged[0].astype(float)
else:
    # If user_id=0 does not exist, create column with NaN
    result[0] = pd.NA

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_26/target_multisource_mcts.csv", index=False)