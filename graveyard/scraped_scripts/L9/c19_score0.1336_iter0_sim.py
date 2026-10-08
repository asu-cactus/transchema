import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

grouped_source1 = source1.groupby('Artist', as_index=False).agg({
    'Year Inducted': 'first',
    'Years Waited': 'first',
    '# of Years Nominated': 'first'
})

joined_1 = pd.merge(grouped_source1, source6, on='Artist', how='outer', suffixes=('', '_src6'))

# Drop duplicate columns from source6 after merge if any
for col in ['Year Inducted_src6', 'Years Waited_src6', '# of Years Nominated_src6']:
    if col in joined_1.columns:
        joined_1.drop(columns=[col], inplace=True)

joined_2 = pd.merge(joined_1, source0, on='Artist', how='outer')
joined_3 = pd.merge(joined_2, source2, on='Artist', how='outer')
joined_4 = pd.merge(joined_3, source3, on='Artist', how='outer')
joined_5 = pd.merge(joined_4, source4, on='Artist', how='outer')
joined_6 = pd.merge(joined_5, source5, on='Artist', how='outer')
joined_7 = pd.merge(joined_6, source7, on='Artist', how='outer')
final_df = pd.merge(joined_7, source8, on='Artist', how='outer')

# Ensure correct dtypes and columns order as per target schema
final_df = final_df.rename(columns={
    'Year Inducted': 'Year Inducted',
    'Years Waited': 'Years Waited',
    '# of Years Nominated': '# of Years Nominated',
    'Inducted By': 'Inducted By',
    'Influenced': 'Influenced',
    'Certified Units (Millions)': 'Certified Units (Millions)',
    'Albums in RS500': 'Albums in RS500',
    'Top 100 Singles': 'Top 100 Singles',
    'Highest Position': 'Highest Position',
    'Times on Cover of RS': 'Times on Cover of RS',
    'Score': 'Score',
    'Spotify': 'Spotify'
})

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