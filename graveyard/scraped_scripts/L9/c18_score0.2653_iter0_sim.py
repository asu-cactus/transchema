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

def pivot_and_rename(df, biz_col, count_col, suffix_biz, suffix_count):
    pivoted = df.pivot_table(index='zipcode', columns=biz_col, values=count_col, aggfunc='sum', fill_value=0)
    pivoted = pivoted.reset_index()
    # Sort columns to have consistent order
    pivoted = pivoted[['zipcode'] + sorted([c for c in pivoted.columns if c != 'zipcode'])]
    # Rename columns to match target pattern
    rename_map = {}
    for i, col in enumerate(pivoted.columns[1:], 1):
        if i == 1:
            rename_map[col] = f'businesses_{suffix_biz}'
            rename_map[col+'_count'] = f'counts_{suffix_count}'
        else:
            rename_map[col] = f'businesses_{suffix_biz}_{i}'
            rename_map[col+'_count'] = f'counts_{suffix_count}_{i}'
    return pivoted

# For source1, source3, source7, source9: pivot businesses and counts to wide format with renamed columns
# We will pivot each source and rename columns to match target columns:
# From target schema and examples, the businesses and counts columns are:
# businesses_x, counts_x (from source9)
# businesses_y, counts_y (from source1)
# businesses_x_5, counts_x_6 (from source3)
# businesses_y_7, counts_y_8 (from source7)
# The suffixes are assigned to match the target columns.

# Pivot source1 (businesses, counts) -> businesses_y, counts_y
pivot1 = source1.pivot_table(index='zipcode', columns='businesses', values='counts', aggfunc='sum').reset_index()
pivot1 = pivot1.rename(columns=lambda x: f'businesses_y' if x == 'businesses' else x)
# Actually, we need to rename columns to businesses_y, counts_y but pivot columns are business names
# So we will rename columns to businesses_y, counts_y by flattening columns:
pivot1 = source1.pivot_table(index='zipcode', columns='businesses', values='counts', aggfunc='sum', fill_value=0).reset_index()
# Rename columns: first column is zipcode, others are business names, we rename them to businesses_y and counts_y with suffixes
# But target has only one businesses_y and counts_y column, so we must select the top business and count per zipcode
# From target examples, businesses_y and counts_y are single string and int, so we must find the business with max counts per zipcode

def get_top_business(df, biz_col, count_col, biz_name_col, count_name_col):
    df_sorted = df.sort_values([biz_col, count_col], ascending=[True, False])
    top = df.groupby('zipcode').apply(lambda g: g.loc[g[count_col].idxmax()]).reset_index(drop=True)
    return top[['zipcode', biz_col, count_col]].rename(columns={biz_col: biz_name_col, count_col: count_name_col})

top1 = get_top_business(source1, 'businesses', 'counts', 'businesses_y', 'counts_y')
top3 = get_top_business(source3, 'businesses', 'counts', 'businesses_x_5', 'counts_x_6')
top7 = get_top_business(source7, 'businesses', 'counts', 'businesses_y_7', 'counts_y_8')
top9 = get_top_business(source9, 'businesses', 'counts', 'businesses_x', 'counts_x')

# Now join these top business tables on zipcode
df = top9.merge(top1, on='zipcode', how='outer')
df = df.merge(top3, on='zipcode', how='outer')
df = df.merge(top7, on='zipcode', how='outer')

# Join source0 (zipcode, total_crime, violation, misdemeanor, felony)
df = df.merge(source0, on='zipcode', how='outer')

# Join source5 (zipcode, theft, assault, harassment)
df = df.merge(source5, on='zipcode', how='outer')

# Join source4 (boro, zipcode)
df = df.merge(source4, on='zipcode', how='left')

# Join source2 (zipcode, indicator, counts)
df = df.merge(source2, on='zipcode', how='outer')

# Join source6 (zipcode, counts) -> counts_x_10 (from target schema)
df = df.merge(source6.rename(columns={'counts': 'counts_x_10'}), on='zipcode', how='outer')

# Rename columns to match target schema exactly
df = df.rename(columns={
    'counts_x': 'counts_x',
    'counts_y': 'counts_y',
    'counts_x_6': 'counts_x_6',
    'counts_y_8': 'counts_y_8',
    'counts_x_10': 'counts_x_10',
    'counts_y_11': 'counts_y_11' if 'counts_y_11' in df.columns else 'counts_y_11',
    'counts': 'counts',
})

# The target schema has counts_y_11 but no source has that column explicitly.
# Possibly counts_y_11 comes from source2 counts? But source2 counts is merged as counts.
# We keep counts_y_11 as NaN if not present.

# Reorder columns to target schema order
target_columns = ['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y',
                  'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8',
                  'boro', 'counts_x_10', 'counts_y_11', 'indicator', 'counts',
                  'total_crime', 'violation', 'misdemeanor', 'felony',
                  'theft', 'assault', 'harassment']

# Some columns may be missing, add them with NaN
for col in target_columns:
    if col not in df.columns:
        df[col] = pd.NA

df = df[target_columns]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)