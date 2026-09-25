import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2], ignore_index=True, sort=False)

merged = pd.merge(union_result, source0[['movie_id', 'title']], on='movie_id', how='inner')

grouped = merged.groupby('title').apply(
    lambda df: pd.Series({
        'F': df.loc[df['gender'] == 'F', 'rating'].mean(),
        'M': df.loc[df['gender'] == 'M', 'rating'].mean()
    })
).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_31/target_multisource_mcts.csv", index=False)