import pandas as pd

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

# Combine all businesses/counts tables (s1, s3, s7, s9) by concatenation
businesses_all = pd.concat([s1, s3, s7, s9], ignore_index=True)

# Pivot businesses_all to wide format with businesses as columns, counts as values, grouped by zipcode
pivot = businesses_all.pivot_table(index='zipcode', columns='businesses', values='counts', aggfunc='sum').reset_index()

# Rename columns to match target schema names
# The target has these business/count columns:
# businesses_x, counts_x, businesses_y, counts_y, businesses_x_5, counts_x_6, businesses_y_7, counts_y_8
# From the example, the businesses columns correspond to:
# businesses_x: Sidewalk Cafe
# businesses_y: Pawnbroker
# businesses_x_5: Debt Collection Agency
# businesses_y_7: Cigarette Retail Dealer
# The counts columns correspond to the counts of these businesses.

# Extract business columns and rename accordingly
pivot = pivot.rename(columns={
    'Sidewalk Cafe': 'counts_x',
    'Pawnbroker': 'counts_y',
    'Debt Collection Agency': 'counts_x_6',
    'Cigarette Retail Dealer': 'counts_y_8'
})

# Add the business name columns as string columns with the business name repeated per row if that business exists in the pivot
# If a business column is missing, create it with NaN counts and NaN business name

def add_business_name_col(df, count_col, business_name_col, business_name):
    if count_col in df.columns:
        df[business_name_col] = business_name
    else:
        df[count_col] = pd.NA
        df[business_name_col] = pd.NA

add_business_name_col(pivot, 'counts_x', 'businesses_x', 'Sidewalk Cafe')
add_business_name_col(pivot, 'counts_y', 'businesses_y', 'Pawnbroker')
add_business_name_col(pivot, 'counts_x_6', 'businesses_x_5', 'Debt Collection Agency')
add_business_name_col(pivot, 'counts_y_8', 'businesses_y_7', 'Cigarette Retail Dealer')

# Reorder columns to put zipcode first
cols_order = ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8']
pivot = pivot[cols_order]

# Join with s4 (boro, zipcode)
joined_1 = pd.merge(pivot, s4, on='zipcode', how='left')

# The target has counts_x_10 and counts_y_11 columns which are not from businesses pivot
# They likely come from s6 and s8 which have counts only, and s6 and s8 have only zipcode and counts
# We will join s6 and s8 and rename their counts columns accordingly

joined_2 = pd.merge(joined_1, s6, on='zipcode', how='left')
joined_2 = joined_2.rename(columns={'counts': 'counts_x_10'})

joined_3 = pd.merge(joined_2, s8, on='zipcode', how='left')
joined_3 = joined_3.rename(columns={'counts': 'counts_y_11'})

# Join with s0 (zipcode, total_crime, violation, misdemeanor, felony)
joined_4 = pd.merge(joined_3, s0, on='zipcode', how='left')

# Join with s2 (zipcode, indicator, counts)
joined_5 = pd.merge(joined_4, s2, on='zipcode', how='left')

# Rename s2 counts to 'counts' as in target
joined_5 = joined_5.rename(columns={'counts': 'counts'})

# Join with s5 (zipcode, theft, assault, harassment)
final = pd.merge(joined_5, s5, on='zipcode', how='left')

# Reorder columns to match target schema exactly
final = final[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
               'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
               'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
               'total_crime', 'violation', 'misdemeanor', 'felony',
               'theft', 'assault', 'harassment']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")