import pandas as pd
import numpy as np

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

# Merge s1 and s6 first (both have Year Inducted etc), outer join on Artist
df = pd.merge(s1, s6, on="Artist", how="outer", suffixes=('', '_drop'))
df = df.loc[:, ~df.columns.str.endswith('_drop')]

# Merge all other tables on Artist with outer join
df = pd.merge(df, s0, on="Artist", how="outer")
df = pd.merge(df, s2, on="Artist", how="outer")
df = pd.merge(df, s3, on="Artist", how="outer")
df = pd.merge(df, s4, on="Artist", how="outer")
df = pd.merge(df, s5, on="Artist", how="outer")
df = pd.merge(df, s7, on="Artist", how="outer")
df = pd.merge(df, s8, on="Artist", how="outer")

# Convert columns to correct types
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

# Define aggregation functions
def first_non_null(series):
    # Return first non-null value or NaN if none
    return series.dropna().iloc[0] if not series.dropna().empty else np.nan

# Aggregate by Artist
agg_df = df.groupby('Artist', dropna=False).agg({
    'Year Inducted': 'mean',  # float
    'Years Waited': 'sum',    # int counts
    '# of Years Nominated': 'sum',  # int counts
    'Inducted By': first_non_null,  # string
    'Influenced': 'sum',      # int counts
    'Certified Units (Millions)': 'mean',  # float
    'Albums in RS500': 'sum',  # int counts
    'Top 100 Singles': 'sum',  # int counts
    'Highest Position': 'sum',  # int counts
    'Times on Cover of RS': 'sum',  # int counts
    'Score': 'mean',          # float
    'Spotify': 'sum'          # int counts
}).reset_index()

# Ensure columns are in target schema order
agg_df = agg_df[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By',
                 'Influenced', 'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles',
                 'Highest Position', 'Times on Cover of RS', 'Score', 'Spotify']]

# Convert dtypes to match target schema
agg_df['Year Inducted'] = agg_df['Year Inducted'].astype(float)
agg_df['Years Waited'] = agg_df['Years Waited'].astype('Int64')
agg_df['# of Years Nominated'] = agg_df['# of Years Nominated'].astype('Int64')
agg_df['Influenced'] = agg_df['Influenced'].astype('Int64')
agg_df['Certified Units (Millions)'] = agg_df['Certified Units (Millions)'].astype(float)
agg_df['Albums in RS500'] = agg_df['Albums in RS500'].astype('Int64')
agg_df['Top 100 Singles'] = agg_df['Top 100 Singles'].astype('Int64')
agg_df['Highest Position'] = agg_df['Highest Position'].astype('Int64')
agg_df['Times on Cover of RS'] = agg_df['Times on Cover of RS'].astype('Int64')
agg_df['Score'] = agg_df['Score'].astype(float)
agg_df['Spotify'] = agg_df['Spotify'].astype('Int64')

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)