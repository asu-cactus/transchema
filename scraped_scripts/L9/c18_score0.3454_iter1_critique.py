import pandas as pd

# Read all sources
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

# Rename business and counts columns in business-count tables to match target schema
# s9: Sidewalk Cafe -> businesses_x, counts_x
s9_renamed = s9.rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'})

# s1: Pawnbroker -> businesses_y, counts_y
s1_renamed = s1.rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'})

# s3: Debt Collection Agency -> businesses_x_5, counts_x_6
s3_renamed = s3.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})

# s7: Cigarette Retail Dealer -> businesses_y_7, counts_y_8
s7_renamed = s7.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

# Start join chain from s0 (main crime data)
df = s0.copy()

# Join s1
df = df.merge(s1_renamed, on='zipcode', how='left')

# Join s3
df = df.merge(s3_renamed, on='zipcode', how='left')

# Join s7
df = df.merge(s7_renamed, on='zipcode', how='left')

# Join s9
df = df.merge(s9_renamed, on='zipcode', how='left')

# Join s4 (boro)
df = df.merge(s4, on='zipcode', how='left')

# Join s2 (indicator, counts)
df = df.merge(s2, on='zipcode', how='left')

# Join s5 (theft, assault, harassment)
df = df.merge(s5, on='zipcode', how='left')

# Join s6 (counts_x_10)
df = df.merge(s6.rename(columns={'counts': 'counts_x_10'}), on='zipcode', how='left')

# Join s8 (counts_y_11)
df = df.merge(s8.rename(columns={'counts': 'counts_y_11'}), on='zipcode', how='left')

# Group by zipcode to ensure uniqueness (no aggregation needed as data is unique per zipcode)
df = df.groupby('zipcode', as_index=False).first()

# Reorder columns to match target schema exactly
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

df = df[cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)