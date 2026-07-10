import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_19/training_8.csv", index_col=0)

# Align columns for union of s1 and s6
# s1 columns: ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated']
# s6 columns: ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']

# Add 'Inducted By' column to s1 with NaN
s1['Inducted By'] = pd.NA

# Ensure consistent dtypes for union
s1 = s1[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']]
s6 = s6[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By']]

# Convert numeric columns to appropriate types
for df in [s1, s6]:
    df['Year Inducted'] = pd.to_numeric(df['Year Inducted'], errors='coerce')
    df['Years Waited'] = pd.to_numeric(df['Years Waited'], errors='coerce').astype('Int64')
    df['# of Years Nominated'] = pd.to_numeric(df['# of Years Nominated'], errors='coerce').astype('Int64')
    # 'Inducted By' is string, no conversion needed

# UNION s1 and s6
union_induction = pd.concat([s1, s6], ignore_index=True)

# Now join union_induction with other sources on 'Artist' using inner join to avoid extra rows
# Convert numeric columns in other sources as needed

# s0
s0['Certified Units (Millions)'] = pd.to_numeric(s0['Certified Units (Millions)'], errors='coerce')

# s2
s2['Spotify'] = pd.to_numeric(s2['Spotify'], errors='coerce').astype('Int64')

# s3
s3['Score'] = pd.to_numeric(s3['Score'], errors='coerce')

# s4
s4['Influenced'] = pd.to_numeric(s4['Influenced'], errors='coerce').astype('Int64')

# s5
s5['Albums in RS500'] = pd.to_numeric(s5['Albums in RS500'], errors='coerce').astype('Int64')

# s7
s7['Top 100 Singles'] = pd.to_numeric(s7['Top 100 Singles'], errors='coerce').astype('Int64')
s7['Highest Position'] = pd.to_numeric(s7['Highest Position'], errors='coerce').astype('Int64')

# s8
s8['Times on Cover of RS'] = pd.to_numeric(s8['Times on Cover of RS'], errors='coerce').astype('Int64')

# Join step by step
result = pd.merge(union_induction, s0, on='Artist', how='inner')
result = pd.merge(result, s2, on='Artist', how='inner')
result = pd.merge(result, s3, on='Artist', how='inner')
result = pd.merge(result, s4, on='Artist', how='inner')
result = pd.merge(result, s5, on='Artist', how='inner')
result = pd.merge(result, s7, on='Artist', how='inner')
result = pd.merge(result, s8, on='Artist', how='inner')

# Convert numeric columns in result to proper types
result['Year Inducted'] = pd.to_numeric(result['Year Inducted'], errors='coerce')
result['Years Waited'] = pd.to_numeric(result['Years Waited'], errors='coerce').astype('Int64')
result['# of Years Nominated'] = pd.to_numeric(result['# of Years Nominated'], errors='coerce').astype('Int64')
result['Influenced'] = pd.to_numeric(result['Influenced'], errors='coerce').astype('Int64')
result['Albums in RS500'] = pd.to_numeric(result['Albums in RS500'], errors='coerce').astype('Int64')
result['Top 100 Singles'] = pd.to_numeric(result['Top 100 Singles'], errors='coerce').astype('Int64')
result['Highest Position'] = pd.to_numeric(result['Highest Position'], errors='coerce').astype('Int64')
result['Times on Cover of RS'] = pd.to_numeric(result['Times on Cover of RS'], errors='coerce').astype('Int64')
result['Certified Units (Millions)'] = pd.to_numeric(result['Certified Units (Millions)'], errors='coerce')
result['Score'] = pd.to_numeric(result['Score'], errors='coerce')
result['Spotify'] = pd.to_numeric(result['Spotify'], errors='coerce').astype('Int64')

# Define aggregation functions
agg_dict = {
    'Year Inducted': 'mean',
    'Years Waited': 'sum',
    '# of Years Nominated': 'sum',
    'Inducted By': 'first',
    'Influenced': 'sum',
    'Certified Units (Millions)': 'mean',
    'Albums in RS500': 'sum',
    'Top 100 Singles': 'sum',
    'Highest Position': 'min',
    'Times on Cover of RS': 'sum',
    'Score': 'mean',
    'Spotify': 'sum'
}

# Group by Artist with aggregations
final = result.groupby('Artist', as_index=False).agg(agg_dict)

# Ensure columns order as target schema
final_cols = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
              'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
              'Times on Cover of RS', 'Score', 'Spotify']

final = final[final_cols]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)