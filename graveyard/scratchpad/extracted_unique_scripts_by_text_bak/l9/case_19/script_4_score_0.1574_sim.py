import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

# Join Source9_19_1 and Source9_19_6 on Artist (both have overlapping columns Year Inducted, Years Waited, # of Years Nominated)
# We keep columns from s6 for these overlapping columns because s6 has Inducted By as well
# Use s6 columns for these overlapping columns, so drop them from s1 before join to avoid duplication
s1_drop = s1.drop(columns=['Year Inducted', 'Years Waited', '# of Years Nominated'], errors='ignore')
result_0 = pd.merge(s1_drop, s6, on='Artist', how='outer')

# Join result_0 with s0 on Artist
result_1 = pd.merge(result_0, s0, on='Artist', how='outer')

# Join result_1 with s2 on Artist
result_2 = pd.merge(result_1, s2, on='Artist', how='outer')

# Join result_2 with s3 on Artist
result_3 = pd.merge(result_2, s3, on='Artist', how='outer')

# Join result_3 with s4 on Artist
result_4 = pd.merge(result_3, s4, on='Artist', how='outer')

# Join result_4 with s5 on Artist
result_5 = pd.merge(result_4, s5, on='Artist', how='outer')

# Join result_5 with s7 on Artist
result_6 = pd.merge(result_5, s7, on='Artist', how='outer')

# Join result_6 with s8 on Artist
result_7 = pd.merge(result_6, s8, on='Artist', how='outer')

# Ensure columns are in target schema order
target_columns = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
                  'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
                  'Times on Cover of RS', 'Score', 'Spotify']

# Some columns may be missing if no data, add them with NaN if needed
for col in target_columns:
    if col not in result_7.columns:
        result_7[col] = pd.NA

result_final = result_7[target_columns]

# Convert data types to match target schema
result_final['Year Inducted'] = pd.to_numeric(result_final['Year Inducted'], errors='coerce')
result_final['Years Waited'] = pd.to_numeric(result_final['Years Waited'], errors='coerce').astype('Int64')
result_final['# of Years Nominated'] = pd.to_numeric(result_final['# of Years Nominated'], errors='coerce').astype('Int64')
result_final['Influenced'] = pd.to_numeric(result_final['Influenced'], errors='coerce').astype('Int64')
result_final['Certified Units (Millions)'] = pd.to_numeric(result_final['Certified Units (Millions)'], errors='coerce')
result_final['Albums in RS500'] = pd.to_numeric(result_final['Albums in RS500'], errors='coerce').astype('Int64')
result_final['Top 100 Singles'] = pd.to_numeric(result_final['Top 100 Singles'], errors='coerce').astype('Int64')
result_final['Highest Position'] = pd.to_numeric(result_final['Highest Position'], errors='coerce').astype('Int64')
result_final['Times on Cover of RS'] = pd.to_numeric(result_final['Times on Cover of RS'], errors='coerce').astype('Int64')
result_final['Score'] = pd.to_numeric(result_final['Score'], errors='coerce')
result_final['Spotify'] = pd.to_numeric(result_final['Spotify'], errors='coerce').astype('Int64')

# Inducted By should be string, keep as is (NaN allowed)

result_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)