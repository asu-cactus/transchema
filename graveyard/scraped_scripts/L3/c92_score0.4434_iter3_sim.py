import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

pivot = source2.pivot_table(index='movie_id', columns='user_id', values='rating', aggfunc='mean').reset_index()
pivot = pivot.melt(id_vars='movie_id', var_name='user_id', value_name='rating').dropna(subset=['rating'])

joined_0_1 = pd.merge(pivot, source0[['movie_id', 'title', 'video_release_date']], on='movie_id', how='left')
joined_0_1_2 = pd.merge(joined_0_1, source1[['user_id', 'age']], on='user_id', how='left')
joined_all = pd.merge(joined_0_1_2, source2[['user_id', 'movie_id', 'unix_timestamp']], on=['user_id', 'movie_id'], how='left')

result = joined_all[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)