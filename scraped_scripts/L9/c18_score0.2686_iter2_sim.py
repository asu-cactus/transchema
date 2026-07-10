import pandas as pd

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

union_df = pd.concat([s1, s3, s7, s9], ignore_index=True)

pivot_df = union_df.pivot_table(index='zipcode', columns='businesses', values='counts', aggfunc='sum').reset_index()
pivot_df.columns.name = None

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)

df = pivot_df.merge(s4, on='zipcode', how='left')
df = df.merge(s0, on='zipcode', how='left')
df = df.merge(s2, on='zipcode', how='left')
df = df.merge(s5, on='zipcode', how='left')
df = df.merge(s6, on='zipcode', how='left', suffixes=('', '_counts_x_10'))
df = df.merge(s8, on='zipcode', how='left', suffixes=('', '_counts_y_11'))

# Rename columns to match target schema
rename_map = {
    'Sidewalk Cafe': 'businesses_x',
    'Pawnbroker': 'businesses_y',
    'Debt Collection Agency': 'businesses_x_5',
    'Cigarette Retail Dealer': 'businesses_y_7',
    'counts': 'counts',
    'counts_x': 'counts_x',
    'counts_y': 'counts_y',
    'counts_x_6': 'counts_x_6',
    'counts_y_8': 'counts_y_8',
    'counts_x_10': 'counts_x_10',
    'counts_y_11': 'counts_y_11'
}

# The pivot columns are the business names, rename them accordingly
# We have to rename the pivoted columns to the target columns:
# The pivot columns are the business names, so rename them to the target columns:
# 'Sidewalk Cafe' -> 'businesses_x' (string column in target, but here it's a count, so we keep counts in counts_x)
# Actually, the target schema has both business names and counts as separate columns.
# We have counts columns from pivot, but business names are constant strings per column.
# So we create business name columns with constant strings matching the pivot columns.

# Create business name columns with constant strings
df['businesses_x'] = 'Sidewalk Cafe'
df['businesses_y'] = 'Pawnbroker'
df['businesses_x_5'] = 'Debt Collection Agency'
df['businesses_y_7'] = 'Cigarette Retail Dealer'

# Rename pivot count columns to target count columns
df = df.rename(columns={
    'Sidewalk Cafe': 'counts_x',
    'Pawnbroker': 'counts_y',
    'Debt Collection Agency': 'counts_x_6',
    'Cigarette Retail Dealer': 'counts_y_8',
    'counts': 'counts',
    'counts_x': 'counts_x',  # from s6 merge, but s6 has only 'counts' column, renamed to counts_x_10 below
    'counts_y': 'counts_y',  # from s8 merge, renamed to counts_y_11 below
})

# The last two merges with s6 and s8 added columns 'counts' and 'counts' with suffixes
# Because of suffixes, the columns are named 'counts' and 'counts_counts_x_10' or 'counts_counts_y_11'
# Actually, suffixes only apply if columns overlap, so let's check columns after merges:

# After merges, s6 'counts' column is renamed to 'counts_x_10'
# After merges, s8 'counts' column is renamed to 'counts_y_11'

# Fix columns from s6 and s8 merges:
if 'counts_x_10' not in df.columns and 'counts' in df.columns:
    df = df.rename(columns={'counts': 'counts_x_10'})
if 'counts_y_11' not in df.columns and 'counts' in df.columns:
    df = df.rename(columns={'counts': 'counts_y_11'})

# The indicator column is from s2, already merged
# The boro column is from s4, already merged

# Reorder columns to match target schema
target_cols = [
    'zipcode',
    'businesses_x', 'counts_x',
    'businesses_y', 'counts_y',
    'businesses_x_5', 'counts_x_6',
    'businesses_y_7', 'counts_y_8',
    'boro', 'counts_x_10', 'counts_y_11',
    'indicator', 'counts',
    'total_crime', 'violation', 'misdemeanor', 'felony',
    'theft', 'assault', 'harassment'
]

# Some columns may be missing if no data, add them with NaN if needed
for col in target_cols:
    if col not in df.columns:
        df[col] = pd.NA

df = df[target_cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv", index=False)