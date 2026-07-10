import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

grouped = df2.groupby('movie_id').agg(
    user_id_mean=('user_id', 'mean'),
    rating_mean=('rating', 'mean'),
    unix_timestamp_mean=('unix_timestamp', 'mean')
).reset_index()

grouped = grouped.merge(df0[['movie_id', 'title']], on='movie_id', how='left')

join_result_1 = grouped.merge(df0, on=['movie_id', 'title'], how='left', suffixes=('', '_drop'))
join_result_1 = join_result_1.drop(columns=[col for col in join_result_1.columns if col.endswith('_drop')])

join_result_2 = join_result_1.merge(df2, on='movie_id', how='left', suffixes=('', '_drop'))
join_result_2 = join_result_2.drop(columns=[col for col in join_result_2.columns if col.endswith('_drop')])

final_join = join_result_2.merge(df1, on='user_id', how='left', suffixes=('', '_drop'))
final_join = final_join.drop(columns=[col for col in final_join.columns if col.endswith('_drop')])

result = pd.DataFrame()
result['title'] = final_join['title']
result['movie_id'] = final_join['movie_id'].astype('Int64')
result['video_release_date'] = pd.to_numeric(final_join['video_release_date'], errors='coerce')
result['user_id'] = final_join['user_id'].astype(float)
result['rating'] = final_join['rating'].astype(float)
result['unix_timestamp'] = final_join['unix_timestamp'].astype(float)
result['age'] = final_join['age'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)