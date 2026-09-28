import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

joined_0 = pd.merge(df0, df1, on="Artist", how="outer")

union_result = pd.concat([joined_0, df2], ignore_index=True, sort=False)

final_df = pd.merge(union_result, df3, on="Artist", how="outer")

final_df = final_df[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

final_df['Year Inducted'] = pd.to_numeric(final_df['Year Inducted'], errors='coerce')
final_df['Years Waited'] = pd.to_numeric(final_df['Years Waited'], errors='coerce').astype('Int64')
final_df['# of Years Nominated'] = pd.to_numeric(final_df['# of Years Nominated'], errors='coerce').astype('Int64')
final_df['Influenced'] = pd.to_numeric(final_df['Influenced'], errors='coerce').astype('Int64')
final_df['Certified Units (Millions)'] = pd.to_numeric(final_df['Certified Units (Millions)'], errors='coerce')

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)