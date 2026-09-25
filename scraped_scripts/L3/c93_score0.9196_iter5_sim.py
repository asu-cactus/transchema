import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_2.csv", index_col=0)

df1 = source1[['movie_id', 'rating']].copy()
df1.rename(columns={'rating': '0'}, inplace=True)

df2 = source2[['movie_id']].copy()
df2['0'] = 0

combined = pd.concat([df1, df2], ignore_index=True)

result = combined.groupby('movie_id', as_index=False)['0'].sum()
result['movie_id'] = result['movie_id'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)