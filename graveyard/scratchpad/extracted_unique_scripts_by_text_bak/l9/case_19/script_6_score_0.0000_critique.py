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

# Drop overlapping columns from s1 to avoid duplication with s6
s1_drop = s1.drop(columns=['Year Inducted', 'Years Waited', '# of Years Nominated'], errors='ignore')

# Join s1 and s6 on Artist using inner join to keep only artists present in both
result_0 = pd.merge(s1_drop, s6, on='Artist', how='inner')

# Join with s0
result_1 = pd.merge(result_0, s0, on='Artist', how='inner')

# Join with s2
result_2 = pd.merge(result_1, s2, on='Artist', how='inner')

# Join with s3
result_3 = pd.merge(result_2, s3, on='Artist', how='inner')

# Join with s4
result_4 = pd.merge(result_3, s4, on='Artist', how='inner')

# Join with s5
result_5 = pd.merge(result_4, s5, on='Artist', how='inner')

# Join with s7
result_6 = pd.merge(result_5, s7, on='Artist', how='inner')

# Join with s8
result_7 = pd.merge(result_6, s8, on='Artist', how='inner')

# Define aggregation functions
def first_non_null(series):
    # Return first non-null value or NaN if none
    return series.dropna().iloc[0] if not series.dropna().empty else pd.NA

agg_dict = {
    'Year Inducted': 'mean',
    'Years Waited': 'mean',
    '# of Years Nominated': 'mean',
    'Inducted By': first_non_null,
    'Influenced': 'sum',
    'Certified Units (Millions)': 'sum',
    'Albums in RS500': 'sum',
    'Top 100 Singles': 'sum',
    'Highest Position': 'min',
    'Times on Cover of RS': 'sum',
    'Score': 'mean',
    'Spotify': 'sum'
}

# Group by Artist and aggregate
result_grouped = result_7.groupby('Artist', as_index=False).agg(agg_dict)

# Ensure columns are in target schema order
target_columns = ['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced',
                  'Certified Units (Millions)', 'Albums in RS500', 'Top 100 Singles', 'Highest Position',
                  'Times on Cover of RS', 'Score', 'Spotify']

# Add missing columns if any (unlikely here)
for col in target_columns:
    if col not in result_grouped.columns:
        result_grouped[col] = pd.NA

result_final = result_grouped[target_columns]

# Convert data types to match target schema
result_final['Year Inducted'] = pd.to_numeric(result_final['Year Inducted'], errors='coerce')
result_final['Years Waited'] = pd.to_numeric(result_final['Years Waited'], errors='coerce').round().astype('Int64')
result_final['# of Years Nominated'] = pd.to_numeric(result_final['# of Years Nominated'], errors='coerce').round().astype('Int64')
result_final['Influenced'] = pd.to_numeric(result_final['Influenced'], errors='coerce').astype('Int64')
result_final['Certified Units (Millions)'] = pd.to_numeric(result_final['Certified Units (Millions)'], errors='coerce')
result_final['Albums in RS500'] = pd.to_numeric(result_final['Albums in RS500'], errors='coerce').astype('Int64')
result_final['Top 100 Singles'] = pd.to_numeric(result_final['Top 100 Singles'], errors='coerce').astype('Int64')
result_final['Highest Position'] = pd.to_numeric(result_final['Highest Position'], errors='coerce').astype('Int64')
result_final['Times on Cover of RS'] = pd.to_numeric(result_final['Times on Cover of RS'], errors='coerce').astype('Int64')
result_final['Score'] = pd.to_numeric(result_final['Score'], errors='coerce')
result_final['Spotify'] = pd.to_numeric(result_final['Spotify'], errors='coerce').astype('Int64')

# Inducted By is string, keep as is (NaN allowed)

result_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_19/target_multisource_mcts.csv", index=False)