import pandas as pd

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

def pivot_businesses(df, businesses_col, counts_col, prefix_business, prefix_counts):
    df_pivot = df.pivot_table(index='zipcode', columns=businesses_col, values=counts_col, aggfunc='sum')
    df_pivot = df_pivot.add_prefix(prefix_business)
    counts = df_pivot.add_prefix('counts_')
    counts = df_pivot.add_prefix(prefix_counts)
    # Actually, we want to keep both business names and counts as separate columns, but target schema shows pairs of business name and counts columns.
    # The target schema has columns like businesses_x, counts_x, businesses_y, counts_y, businesses_x_5, counts_x_6, businesses_y_7, counts_y_8
    # From source1,3,7,9 we have businesses and counts columns. We need to assign them accordingly.
    # We'll extract top businesses per zipcode from each source and rename columns accordingly.

    # Instead of pivoting all businesses, we will extract top business and counts per source to match target columns.

    return df_pivot

# For source1, source3, source7, source9, we want to extract top business and counts per zipcode.
# The target columns suggest 4 pairs of businesses and counts from these sources:
# businesses_x, counts_x  (from source9: Sidewalk Cafe)
# businesses_y, counts_y  (from source1: Pawnbroker)
# businesses_x_5, counts_x_6 (from source3: Debt Collection Agency)
# businesses_y_7, counts_y_8 (from source7: Cigarette Retail Dealer)

# So we will extract from each source the business with max counts per zipcode (or the only business per zipcode if unique),
# and rename columns accordingly.

def extract_business_counts(df, business_col, counts_col, biz_col_name, counts_col_name):
    # For each zipcode, get the business and counts
    # If multiple businesses per zipcode, pick the one with max counts
    idx = df.groupby('zipcode')[counts_col].idxmax()
    df_top = df.loc[idx, ['zipcode', business_col, counts_col]].copy()
    df_top = df_top.rename(columns={business_col: biz_col_name, counts_col: counts_col_name})
    return df_top

source1_top = extract_business_counts(source1, 'businesses', 'counts', 'businesses_y', 'counts_y')
source3_top = extract_business_counts(source3, 'businesses', 'counts', 'businesses_x_5', 'counts_x_6')
source7_top = extract_business_counts(source7, 'businesses', 'counts', 'businesses_y_7', 'counts_y_8')
source9_top = extract_business_counts(source9, 'businesses', 'counts', 'businesses_x', 'counts_x')

# Now join source1_top and source3_top on zipcode
joined_1_3 = pd.merge(source1_top, source3_top, on='zipcode', how='outer')

# Join with source4 (boro, zipcode)
joined_1_3_4 = pd.merge(joined_1_3, source4, on='zipcode', how='outer')

# Join with source0 (zipcode, total_crime, violation, misdemeanor, felony)
joined_1_3_4_0 = pd.merge(joined_1_3_4, source0, on='zipcode', how='outer')

# Join with source5 (zipcode, theft, assault, harassment)
joined_1_3_4_0_5 = pd.merge(joined_1_3_4_0, source5, on='zipcode', how='outer')

# Join with source6 (zipcode, counts) -> rename counts to counts_x_10 to match target
source6_renamed = source6.rename(columns={'counts': 'counts_x_10'})
joined_1_3_4_0_5_6 = pd.merge(joined_1_3_4_0_5, source6_renamed, on='zipcode', how='outer')

# Join with source8 (zipcode, counts) -> rename counts to counts_y_11
source8_renamed = source8.rename(columns={'counts': 'counts_y_11'})
joined_1_3_4_0_5_6_8 = pd.merge(joined_1_3_4_0_5_6, source8_renamed, on='zipcode', how='outer')

# Join with source2 (zipcode, indicator, counts)
source2_renamed = source2.rename(columns={'counts': 'counts'})
joined_1_3_4_0_5_6_8_2 = pd.merge(joined_1_3_4_0_5_6_8, source2_renamed, on='zipcode', how='outer')

# Join with source7_top (already joined?), no, source7_top was joined earlier? No, source7_top was joined with source1_top and source3_top? No, only source1_top and source3_top joined.
# So join source7_top now:
joined_1_3_4_0_5_6_8_2_7 = pd.merge(joined_1_3_4_0_5_6_8_2, source7_top, on='zipcode', how='outer')

# Join with source9_top (businesses_x, counts_x)
final_join = pd.merge(joined_1_3_4_0_5_6_8_2_7, source9_top, on='zipcode', how='outer')

# The above merges may have duplicated columns for businesses_x and counts_x from source9_top and source9_top was already used? Actually source9_top was used only now.

# The target schema columns:
# ['zipcode': int,
#  'businesses_x': str, 'counts_x': int,
#  'businesses_y': str, 'counts_y': int,
#  'businesses_x_5': str, 'counts_x_6': int,
#  'businesses_y_7': str, 'counts_y_8': int,
#  'boro': str,
#  'counts_x_10': int,
#  'counts_y_11': int,
#  'indicator': str,
#  'counts': int,
#  'total_crime': int,
#  'violation': int,
#  'misdemeanor': int,
#  'felony': int,
#  'theft': int,
#  'assault': int,
#  'harassment': int]

# Some columns may be missing or have NaNs, keep as is.

# Reorder columns to match target schema
final_cols = ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
              'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
              'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
              'total_crime', 'violation', 'misdemeanor', 'felony',
              'theft', 'assault', 'harassment']

result = final_join[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")