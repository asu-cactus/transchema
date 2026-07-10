import pandas as pd

# Read sources
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)

# Union the four large source tables with the same schema
union_df = pd.concat([src0, src2, src6, src7], ignore_index=True)

# Convert numeric columns to proper types before aggregation
union_df['ARPU'] = pd.to_numeric(union_df['ARPU'], errors='coerce')
union_df['MONTHS_AGE'] = pd.to_numeric(union_df['MONTHS_AGE'], errors='coerce')
union_df['CANCELED'] = pd.to_numeric(union_df['CANCELED'], errors='coerce').astype('Int64')
union_df['ROW_WID'] = pd.to_numeric(union_df['ROW_WID'], errors='coerce').astype('Int64')
union_df['ACCNT_LOC'] = pd.to_numeric(union_df['ACCNT_LOC'], errors='coerce').astype('Int64')
union_df['HOME_PASSED'] = pd.to_numeric(union_df['HOME_PASSED'], errors='coerce').astype('Int64')

# Group by key columns and aggregate ARPU and MONTHS_AGE by mean
group_cols = ['ROW_WID', 'CANCELED', 'ACCNT_LOC', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']
agg_df = union_df.groupby(group_cols, dropna=False).agg({
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean'
}).reset_index()

# Join with other source tables on ROW_WID
df = agg_df.merge(src1, on='ROW_WID', how='left')
df = df.merge(src3, on='ROW_WID', how='left')
df = df.merge(src4, on='ROW_WID', how='left')
df = df.merge(src5, on='ROW_WID', how='left')
df = df.merge(src8, on='ROW_WID', how='left')
df = df.merge(src9, on='ROW_WID', how='left')

# Fill NaN in numeric columns from aspect tables with 0
for col in ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')

# Now group again to aggregate the numeric columns by sum, grouping by all non-numeric and key columns plus ARPU and MONTHS_AGE
final_group_cols = group_cols + ['ARPU', 'MONTHS_AGE']
sum_cols = ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df.groupby(final_group_cols, dropna=False)[sum_cols].sum().reset_index()

# Reorder columns to match target schema
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Merge back the group columns to get SES and other string columns (since they are in group cols)
# The groupby reset_index keeps these columns, so just reorder
df = df[cols]

# Convert types to match target schema
df['ARPU'] = pd.to_numeric(df['ARPU'], errors='coerce')
df['MONTHS_AGE'] = pd.to_numeric(df['MONTHS_AGE'], errors='coerce')
df['CANCELED'] = pd.to_numeric(df['CANCELED'], errors='coerce').astype('Int64')
df['ROW_WID'] = pd.to_numeric(df['ROW_WID'], errors='coerce').astype('Int64')
df['ACCNT_LOC'] = pd.to_numeric(df['ACCNT_LOC'], errors='coerce').astype('Int64')
df['HOME_PASSED'] = pd.to_numeric(df['HOME_PASSED'], errors='coerce').astype('Int64')

for col in ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')

# Convert string columns
for col in ['SES', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']:
    df[col] = df[col].astype(str)

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)