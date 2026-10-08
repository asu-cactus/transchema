import pandas as pd

s3_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_0.csv", index_col=0)
s3_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_1.csv", index_col=0)
s3_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_2.csv", index_col=0)
s3_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_3.csv", index_col=0)
s3_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_4.csv", index_col=0)
s3_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_5.csv", index_col=0)

union_result = pd.concat([s3_3, s3_5], ignore_index=True, sort=False)

join_result_1 = pd.merge(union_result, s3_0, on="Artist", how="outer")
join_result_2 = pd.merge(join_result_1, s3_1, on="Artist", how="outer")
join_result_3 = pd.merge(join_result_2, s3_2, on="Artist", how="outer")
final_df = pd.merge(join_result_3, s3_4, on="Artist", how="outer")

final_df = final_df[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position']]

final_df['Year Inducted'] = pd.to_numeric(final_df['Year Inducted'], errors='coerce')
final_df['Years Waited'] = pd.to_numeric(final_df['Years Waited'], errors='coerce').astype('Int64')
final_df['# of Years Nominated'] = pd.to_numeric(final_df['# of Years Nominated'], errors='coerce').astype('Int64')
final_df['Influenced'] = pd.to_numeric(final_df['Influenced'], errors='coerce').astype('Int64')
final_df['Certified Units (Millions)'] = pd.to_numeric(final_df['Certified Units (Millions)'], errors='coerce')
final_df['Albums in RS500'] = pd.to_numeric(final_df['Albums in RS500'], errors='coerce').astype('Int64')
final_df['Top 100 Singles'] = pd.to_numeric(final_df['Top 100 Singles'], errors='coerce').astype('Int64')
final_df['Highest Position'] = pd.to_numeric(final_df['Highest Position'], errors='coerce').astype('Int64')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_3/target_multisource_mcts.csv", index=False)