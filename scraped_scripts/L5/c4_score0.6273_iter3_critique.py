import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

# Join Source5_4_0 and Source5_4_1 on Artist (inner join to keep only artists present in both)
join_0_1 = pd.merge(s0, s1, on="Artist", how="inner")

# Join the above result with Source5_4_2 on Artist (left join to keep all artists from join_0_1)
join_0_1_2 = pd.merge(join_0_1, s2, on="Artist", how="left", suffixes=('', '_drop'))

# Drop duplicate columns from suffix '_drop' if any
join_0_1_2 = join_0_1_2.drop(columns=[col for col in join_0_1_2.columns if col.endswith('_drop')])

# Join the above result with Source5_4_3 on Artist (left join to keep all artists from previous join)
final_join = pd.merge(join_0_1_2, s3, on="Artist", how="left")

# Group by Artist to ensure uniqueness (no aggregation needed as Artist is unique key)
final = final_join.groupby('Artist', as_index=False).first()

# Reorder columns to match target schema exactly
final = final[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

# Convert columns to correct types
final['Year Inducted'] = pd.to_numeric(final['Year Inducted'], errors='coerce')
final['Years Waited'] = pd.to_numeric(final['Years Waited'], errors='coerce').astype('Int64')
final['# of Years Nominated'] = pd.to_numeric(final['# of Years Nominated'], errors='coerce').astype('Int64')
final['Influenced'] = pd.to_numeric(final['Influenced'], errors='coerce').astype('Int64')
final['Certified Units (Millions)'] = pd.to_numeric(final['Certified Units (Millions)'], errors='coerce')

# Write final output
final.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)