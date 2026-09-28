import pandas as pd

# Read sources with index_col=0 to ignore the first index column
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
source5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
source7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

def extract_top_business_counts(df, business_col, counts_col, biz_col_name, counts_col_name):
    # For each zipcode, get the business and counts with max counts
    idx = df.groupby('zipcode')[counts_col].idxmax()
    df_top = df.loc[idx, ['zipcode', business_col, counts_col]].copy()
    df_top = df_top.rename(columns={business_col: biz_col_name, counts_col: counts_col_name})
    return df_top

# Extract top business/count pairs from sources with businesses/counts columns
source1_top = extract_top_business_counts(source1, 'businesses', 'counts', 'businesses_y', 'counts_y')  # Pawnbroker
source3_top = extract_top_business_counts(source3, 'businesses', 'counts', 'businesses_x_5', 'counts_x_6')  # Debt Collection Agency
source7_top = extract_top_business_counts(source7, 'businesses', 'counts', 'businesses_y_7', 'counts_y_8')  # Cigarette Retail Dealer
source9_top = extract_top_business_counts(source9, 'businesses', 'counts', 'businesses_x', 'counts_x')  # Sidewalk Cafe

# Rename counts columns in source6 and source8 to match target schema
source6_renamed = source6.rename(columns={'counts': 'counts_x_10'})
source8_renamed = source8.rename(columns={'counts': 'counts_y_11'})

# Join all sources step by step on 'zipcode' using INNER JOIN to keep only zipcodes present in all sources
# Start from source0 (main crime data)
df = source0.copy()

# Join with source1_top
df = pd.merge(df, source1_top, on='zipcode', how='inner')

# Join with source3_top
df = pd.merge(df, source3_top, on='zipcode', how='inner')

# Join with source4 (boro)
df = pd.merge(df, source4, on='zipcode', how='inner')

# Join with source5 (theft, assault, harassment)
df = pd.merge(df, source5, on='zipcode', how='inner')

# Join with source6_renamed (counts_x_10)
df = pd.merge(df, source6_renamed, on='zipcode', how='inner')

# Join with source7_top
df = pd.merge(df, source7_top, on='zipcode', how='inner')

# Join with source8_renamed (counts_y_11)
df = pd.merge(df, source8_renamed, on='zipcode', how='inner')

# Join with source9_top
df = pd.merge(df, source9_top, on='zipcode', how='inner')

# Join with source2 (indicator, counts)
df = pd.merge(df, source2, on='zipcode', how='inner')

# Rename source2 'counts' column to 'counts' (already named counts)
# No rename needed

# Reorder columns to match target schema exactly
final_cols = ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
              'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
              'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
              'total_crime', 'violation', 'misdemeanor', 'felony',
              'theft', 'assault', 'harassment']

result = df[final_cols]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")