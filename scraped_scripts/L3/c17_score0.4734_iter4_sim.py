import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_2.csv", index_col=0)

union_result = pd.concat([source0, source2], ignore_index=True, sort=False)

joined = union_result.merge(source1[['movie_id', 'title']], on='movie_id', how='inner')

grouped = joined.groupby('title').apply(
    lambda df: pd.Series({
        'F': df.loc[df['gender'] == 'F', 'rating'].mean() if 'gender' in df else None,
        'M': df.loc[df['gender'] == 'M', 'rating'].mean() if 'gender' in df else None
    })
).reset_index()

grouped['F'] = grouped['F'].astype(float)
grouped['M'] = grouped['M'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_17/target_multisource_mcts.csv", index=False)