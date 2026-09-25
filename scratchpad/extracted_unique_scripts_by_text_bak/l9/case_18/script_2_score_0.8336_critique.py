import pandas as pd

# Read all sources with index_col=0 to ignore the first index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

# Rename business tables columns to match target schema
u9 = s9.rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'})
u1 = s1.rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'})
u3 = s3.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})
u7 = s7.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

# Rename counts-only tables columns
s6_renamed = s6.rename(columns={'counts': 'counts_x_10'})
s8_renamed = s8.rename(columns={'counts': 'counts_y_11'})

# Start joining business tables on zipcode with inner joins to keep only zipcodes present in all
df = pd.merge(u9, u1, on='zipcode', how='inner')
df = pd.merge(df, u3, on='zipcode', how='inner')
df = pd.merge(df, u7, on='zipcode', how='inner')

# Join counts-only tables
df = pd.merge(df, s6_renamed, on='zipcode', how='inner')
df = pd.merge(df, s8_renamed, on='zipcode', how='inner')

# Join boro
df = pd.merge(df, s4, on='zipcode', how='inner')

# Join crime stats
df = pd.merge(df, s0, on='zipcode', how='inner')

# Join theft, assault, harassment
df = pd.merge(df, s5, on='zipcode', how='inner')

# Join indicator and counts
df = pd.merge(df, s2, on='zipcode', how='inner')

# Group by zipcode to ensure uniqueness and aggregate counts by sum, strings by first
agg_dict = {
    'businesses_x': 'first',
    'counts_x': 'sum',
    'businesses_y': 'first',
    'counts_y': 'sum',
    'businesses_x_5': 'first',
    'counts_x_6': 'sum',
    'businesses_y_7': 'first',
    'counts_y_8': 'sum',
    'boro': 'first',
    'counts_x_10': 'sum',
    'counts_y_11': 'sum',
    'indicator': 'first',
    'counts': 'sum',
    'total_crime': 'sum',
    'violation': 'sum',
    'misdemeanor': 'sum',
    'felony': 'sum',
    'theft': 'sum',
    'assault': 'sum',
    'harassment': 'sum'
}

df_final = df.groupby('zipcode', as_index=False).agg(agg_dict)

# Reorder columns exactly as target schema
cols = ['zipcode',
        'businesses_x', 'counts_x',
        'businesses_y', 'counts_y',
        'businesses_x_5', 'counts_x_6',
        'businesses_y_7', 'counts_y_8',
        'boro',
        'counts_x_10', 'counts_y_11',
        'indicator', 'counts',
        'total_crime', 'violation', 'misdemeanor', 'felony',
        'theft', 'assault', 'harassment']

df_final = df_final[cols]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)