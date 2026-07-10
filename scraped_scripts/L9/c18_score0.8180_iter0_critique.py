import pandas as pd

# Read sources with index_col=0 to ignore the first numerical index column
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

# Rename businesses and counts columns in each source with (zipcode, businesses, counts) schema to unique names matching target schema

# source9 -> businesses_x, counts_x
source9_renamed = source9.rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'})

# source1 -> businesses_y, counts_y
source1_renamed = source1.rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'})

# source3 -> businesses_x_5, counts_x_6
source3_renamed = source3.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})

# source7 -> businesses_y_7, counts_y_8
source7_renamed = source7.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

# source4 has (boro, zipcode), rename zipcode to keep consistent join key
# Actually, source4 already has zipcode column, no rename needed

# source2 has (zipcode, indicator, counts)
# counts column in source2 corresponds to 'counts' in target schema
# indicator column matches target

# source6 has (zipcode, counts) -> counts_x_10 in target
source6_renamed = source6.rename(columns={'counts': 'counts_x_10'})

# source8 has (zipcode, counts) but target schema does not have a direct mapping for source8 counts
# The target schema has counts_y_11 which is not clearly mapped
# Possibly counts_y_11 comes from source8 counts
source8_renamed = source8.rename(columns={'counts': 'counts_y_11'})

# Start joining step by step with inner joins on zipcode to keep only zipcodes present in all

df = source9_renamed.merge(source1_renamed, on='zipcode', how='inner')
df = df.merge(source3_renamed, on='zipcode', how='inner')
df = df.merge(source7_renamed, on='zipcode', how='inner')
df = df.merge(source0, on='zipcode', how='inner')
df = df.merge(source5, on='zipcode', how='inner')
df = df.merge(source4, on='zipcode', how='inner')
df = df.merge(source2, on='zipcode', how='inner')
df = df.merge(source6_renamed, on='zipcode', how='inner')
df = df.merge(source8_renamed, on='zipcode', how='inner')

# Reorder columns exactly as target schema
target_columns = ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
                  'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
                  'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
                  'total_crime', 'violation', 'misdemeanor', 'felony',
                  'theft', 'assault', 'harassment']

# Some columns may be missing if source8 or others have missing data, add them with NaN
for col in target_columns:
    if col not in df.columns:
        df[col] = pd.NA

df = df[target_columns]

# Ensure correct dtypes for zipcode (int) and counts (int), others as object or string as needed
# Convert zipcode to int if possible
df['zipcode'] = df['zipcode'].astype(int)

# Convert counts columns to integer if possible, else keep as is (some may have NaN)
count_cols = ['counts_x', 'counts_y', 'counts_x_6', 'counts_y_8', 'counts_x_10', 'counts_y_11', 'counts', 
              'total_crime', 'violation', 'misdemeanor', 'felony', 'theft', 'assault', 'harassment']

for col in count_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Write to CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)