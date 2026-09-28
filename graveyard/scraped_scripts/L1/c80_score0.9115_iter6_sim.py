import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

joined = pd.merge(df, df, left_on='userId', right_on='userId', suffixes=('_left', '_right'))

result = joined.groupby('movieId_left', as_index=False)['rating_left'].mean()
result.columns = ['movieId', 'rating']
result['movieId'] = result['movieId'].astype(int)
result['rating'] = result['rating'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)