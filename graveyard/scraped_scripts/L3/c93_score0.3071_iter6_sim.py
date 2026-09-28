import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_93/training_2.csv", index_col=0)

df1 = source1[['movie_id', 'rating']].copy()
df2 = source2[['movie_id']].copy()
df2['rating'] = 0
df0 = source0.copy()
df0.rename(columns={'user_id': 'movie_id'}, inplace=True)
df0 = df0[['movie_id']]
df0['rating'] = 0

union_1_2 = pd.concat([df1, df2], ignore_index=True, sort=False)
union_all = pd.concat([union_1_2, df0], ignore_index=True, sort=False)

union_all.rename(columns={'rating': '0'}, inplace=True)
union_all = union_all[['movie_id', '0']]
union_all['movie_id'] = union_all['movie_id'].astype('Int64')
union_all['0'] = union_all['0'].astype('Int64')

union_all.to_csv("autopipeline-benchmarks/github-pipelines/length3_93/target_multisource_mcts.csv", index=False)