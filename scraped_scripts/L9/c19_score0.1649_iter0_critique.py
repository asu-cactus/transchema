import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

# Union source1 and source6
# source1 lacks 'Inducted By' column, add it with NaN to align schemas
source1_extended = source1.copy()
source1_extended['Inducted By'] = pd.NA

union_1_6 = pd.concat([source1_extended, source6], ignore_index=True, sort=False)

# Join union_1_6 with source0 on 'Artist' (outer join to keep all artists)
joined_0 = pd.merge(union_1_6, source0, on='Artist', how='outer')

# Join with source2
joined_1 = pd.merge(joined_0, source2, on='Artist', how='outer')

# Join with source3
joined_2 = pd.merge(joined_1, source3, on='Artist', how='outer')

# Join with source4
joined_3 = pd.merge(joined_2, source4, on='Artist', how='outer')

# Join with source5
joined_4 = pd.merge(joined_3, source5, on='Artist', how='outer')

# Join with source7
joined_5 = pd.merge(joined_4, source7, on='Artist', how='outer')

# Join with source8
joined_6 = pd.merge(joined_5, source8, on='Artist', how='outer')

# Now group by 'Artist' and aggregate as per plan
agg_dict = {
    'Year Inducted': 'first',
    'Years Waited': 'first',
    '# of Years Nominated': 'first',
    'Inducted By': 'first',
    'Influenced': 'sum',
    'Certified Units (Millions)': 'sum',
    'Albums in RS500': 'sum',
    'Top 100 Singles': 'sum',
    'Highest Position': 'sum',
    'Times on Cover of RS': 'sum',
    'Score': 'mean',
    'Spotify': 'sum'
}

final_df = joined_6.groupby('Artist', as_index=False).agg(agg_dict)

# Ensure correct dtypes as per target schema
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

# Reorder columns as per target schema
cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
        'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
        'Times on Cover of RS', 'Score', 'Spotify']

final_df = final_df[cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)