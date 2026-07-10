import pandas as pd

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
union_result = pd.concat([s1, s6], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, s0, on="Artist", how="outer")

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s2, on="Artist", how="outer")

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, s3, on="Artist", how="outer")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
join_result_4 = pd.merge(join_result_3, s4, on="Artist", how="outer")

s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
join_result_5 = pd.merge(join_result_4, s5, on="Artist", how="outer")

s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
join_result_6 = pd.merge(join_result_5, s7, on="Artist", how="outer")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)
final_df = pd.merge(join_result_6, s8, on="Artist", how="outer")

cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
        'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
        'Times on Cover of RS', 'Score', 'Spotify']

final_df = final_df[cols]

final_df['Year Inducted'] = pd.to_numeric(final_df['Year Inducted'], errors='coerce')
final_df['Years Waited'] = pd.to_numeric(final_df['Years Waited'], errors='coerce').astype('Int64')
final_df['# of Years Nominated'] = pd.to_numeric(final_df['# of Years Nominated'], errors='coerce').astype('Int64')
final_df['Influenced'] = pd.to_numeric(final_df['Influenced'], errors='coerce').astype('Int64')
final_df['Certified Units (Millions)'] = pd.to_numeric(final_df['Certified Units (Millions)'], errors='coerce')
final_df['Albums in RS500'] = pd.to_numeric(final_df['Albums in RS500'], errors='coerce').astype('Int64')
final_df['Top 100 Singles'] = pd.to_numeric(final_df['Top 100 Singles'], errors='coerce').astype('Int64')
final_df['Highest Position'] = pd.to_numeric(final_df['Highest Position'], errors='coerce').astype('Int64')
final_df['Times on Cover of RS'] = pd.to_numeric(final_df['Times on Cover of RS'], errors='coerce').astype('Int64')
final_df['Score'] = pd.to_numeric(final_df['Score'], errors='coerce')
final_df['Spotify'] = pd.to_numeric(final_df['Spotify'], errors='coerce').astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)