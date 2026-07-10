import pandas as pd
import numpy as np

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

# Join Source9_19_1 and Source9_19_6 on Artist (outer join to keep all)
df_1_6 = pd.merge(s1, s6, on="Artist", how="outer", suffixes=('_1', '_6'))

# After merge, columns from s1: ['Artist', 'Year Inducted_1', 'Years Waited_1', '# of Years Nominated_1']
# Columns from s6: ['Artist', 'Year Inducted_6', 'Years Waited_6', '# of Years Nominated_6', 'Inducted By']

# We need to combine the duplicate columns by taking the mean or coalesce:
def coalesce_cols(df, col1, col2):
    return df[col1].combine_first(df[col2])

df_1_6['Year Inducted'] = pd.to_numeric(coalesce_cols(df_1_6, 'Year Inducted_6', 'Year Inducted_1'), errors='coerce')
df_1_6['Years Waited'] = pd.to_numeric(coalesce_cols(df_1_6, 'Years Waited_6', 'Years Waited_1'), errors='coerce')
df_1_6['# of Years Nominated'] = pd.to_numeric(coalesce_cols(df_1_6, '# of Years Nominated_6', '# of Years Nominated_1'), errors='coerce')
df_1_6['Inducted By'] = df_1_6['Inducted By']  # only in s6

# Drop old columns
df_1_6 = df_1_6.drop(columns=['Year Inducted_1', 'Year Inducted_6', 'Years Waited_1', 'Years Waited_6',
                              '# of Years Nominated_1', '# of Years Nominated_6'])

# Join with s0
df = pd.merge(df_1_6, s0, on="Artist", how="outer")

# Join with s2
df = pd.merge(df, s2, on="Artist", how="outer")

# Join with s3
df = pd.merge(df, s3, on="Artist", how="outer")

# Join with s4
df = pd.merge(df, s4, on="Artist", how="outer")

# Join with s5
df = pd.merge(df, s5, on="Artist", how="outer")

# Join with s7
df = pd.merge(df, s7, on="Artist", how="outer")

# Join with s8
df = pd.merge(df, s8, on="Artist", how="outer")

# Convert columns to appropriate types
df['Year Inducted'] = pd.to_numeric(df['Year Inducted'], errors='coerce')
df['Years Waited'] = pd.to_numeric(df['Years Waited'], errors='coerce').astype('Int64')
df['# of Years Nominated'] = pd.to_numeric(df['# of Years Nominated'], errors='coerce').astype('Int64')
df['Influenced'] = pd.to_numeric(df['Influenced'], errors='coerce').astype('Int64')
df['Certified Units (Millions)'] = pd.to_numeric(df['Certified Units (Millions)'], errors='coerce')
df['Albums in RS500'] = pd.to_numeric(df['Albums in RS500'], errors='coerce').astype('Int64')
df['Top 100 Singles'] = pd.to_numeric(df['Top 100 Singles'], errors='coerce').astype('Int64')
df['Highest Position'] = pd.to_numeric(df['Highest Position'], errors='coerce').astype('Int64')
df['Times on Cover of RS'] = pd.to_numeric(df['Times on Cover of RS'], errors='coerce').astype('Int64')
df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
df['Spotify'] = pd.to_numeric(df['Spotify'], errors='coerce').astype('Int64')

# Group by Artist to ensure uniqueness, aggregate as per column type and semantics
agg_dict = {
    'Year Inducted': 'mean',  # float, average year
    'Years Waited': 'mean',   # integer, average wait
    '# of Years Nominated': 'mean',  # integer, average nominations
    'Inducted By': 'first',   # string, take first non-null
    'Influenced': 'sum',      # integer count
    'Certified Units (Millions)': 'mean',  # float, average units
    'Albums in RS500': 'sum',  # integer count
    'Top 100 Singles': 'sum',  # integer count
    'Highest Position': 'min', # integer, best position (lowest)
    'Times on Cover of RS': 'sum',  # integer count
    'Score': 'mean',          # float average score
    'Spotify': 'sum'          # integer count
}

final_df = df.groupby('Artist', dropna=False, as_index=False).agg(agg_dict)

# Reorder columns as per target schema
cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
        'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
        'Times on Cover of RS', 'Score', 'Spotify']

final_df = final_df[cols]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)