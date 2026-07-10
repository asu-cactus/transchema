import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_3/training_5.csv", index_col=0)

# Join s3 and s5 on Artist (both have Year Inducted etc., prefer s5's columns)
join_0 = pd.merge(s3, s5, on="Artist", how="inner", suffixes=('_3', '_5'))

# After join_0, drop s3's columns for Year Inducted, Years Waited, # of Years Nominated to avoid duplication
join_0 = join_0.drop(columns=['Year Inducted_3', 'Years Waited_3', '# of Years Nominated_3'])

# Rename s5 columns to original names (they are already named correctly)
join_0 = join_0.rename(columns={
    'Year Inducted_5': 'Year Inducted',
    'Years Waited_5': 'Years Waited',
    '# of Years Nominated_5': '# of Years Nominated'
})

# Join with s0
join_1 = pd.merge(join_0, s0, on="Artist", how="inner")

# Join with s1
join_2 = pd.merge(join_1, s1, on="Artist", how="inner")

# Join with s2
join_3 = pd.merge(join_2, s2, on="Artist", how="inner")

# Join with s4
final_join = pd.merge(join_3, s4, on="Artist", how="inner")

# Define aggregation functions
agg_dict = {
    'Year Inducted': 'max',
    'Years Waited': 'max',
    '# of Years Nominated': 'max',
    'Inducted By': 'first',
    'Influenced': 'sum',
    'Certified Units (Millions)': 'sum',
    'Albums in RS500': 'sum',
    'Top 100 Singles': 'sum',
    'Highest Position': 'min'
}

# Group by Artist and aggregate
final = final_join.groupby('Artist', as_index=False).agg(agg_dict)

# Convert columns to correct types
final['Year Inducted'] = pd.to_numeric(final['Year Inducted'], errors='coerce')
final['Years Waited'] = pd.to_numeric(final['Years Waited'], errors='coerce').astype('Int64')
final['# of Years Nominated'] = pd.to_numeric(final['# of Years Nominated'], errors='coerce').astype('Int64')
final['Influenced'] = pd.to_numeric(final['Influenced'], errors='coerce').astype('Int64')
final['Certified Units (Millions)'] = pd.to_numeric(final['Certified Units (Millions)'], errors='coerce')
final['Albums in RS500'] = pd.to_numeric(final['Albums in RS500'], errors='coerce').astype('Int64')
final['Top 100 Singles'] = pd.to_numeric(final['Top 100 Singles'], errors='coerce').astype('Int64')
final['Highest Position'] = pd.to_numeric(final['Highest Position'], errors='coerce').astype('Int64')

# Reorder columns to match target schema
cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By',
        'Influenced', 'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position']

final = final[cols]

# Write to CSV
final.to_csv("autopipeline-benchmarks/github-pipelines/length5_3/target_multisource_mcts.csv", index=False)