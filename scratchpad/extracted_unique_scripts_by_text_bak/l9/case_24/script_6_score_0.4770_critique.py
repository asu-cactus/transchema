import pandas as pd

# Read dimension tables with same schema
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)

# Union dimension tables
union_dim = pd.concat([s0, s2, s6, s7], ignore_index=True)

# Group by key columns to remove duplicates and aggregate float columns by mean
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']
agg_dict = {
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean'
}

# For columns in group_by_cols that are strings, keep first (they should be identical per group)
# So groupby with agg for floats, and first for others
# Prepare aggregation dictionary for all columns
for col in group_by_cols:
    if col not in agg_dict:
        agg_dict[col] = 'first'

union_grouped = union_dim.groupby(group_by_cols, as_index=False).agg(agg_dict)

# Read aspect tables with *_NUM columns
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)  # KEYWORDS_NUM
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)  # VISITS_NUM
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)  # COLLECTION_EVENTS_NUM
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)  # TECHSUPPORT_NUM
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)  # INBOUND_CALLS_NUM
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)  # INTERACTIONS_NUM

# Join all aspect tables on ROW_WID with left join to keep all dimension rows
df = union_grouped.merge(s1, on='ROW_WID', how='left')
df = df.merge(s3, on='ROW_WID', how='left')
df = df.merge(s4, on='ROW_WID', how='left')
df = df.merge(s5, on='ROW_WID', how='left')
df = df.merge(s8, on='ROW_WID', how='left')
df = df.merge(s9, on='ROW_WID', how='left')

# Select columns in target order
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

# Cast types as per target schema
df['CANCELED'] = df['CANCELED'].astype('Int64')
df['ROW_WID'] = df['ROW_WID'].astype('Int64')
df['ACCNT_LOC'] = df['ACCNT_LOC'].astype('Int64')
df['ARPU'] = df['ARPU'].astype(float)
df['SES'] = df['SES'].astype(str)
df['HOME_PASSED'] = df['HOME_PASSED'].astype('Int64')
df['CUST_SINCE_DT'] = df['CUST_SINCE_DT'].astype(str)
df['MONTHS_AGE'] = df['MONTHS_AGE'].astype(float)
df['CANCEL_DT'] = df['CANCEL_DT'].astype(str)
df['CITY'] = df['CITY'].astype(str)
df['POP'] = df['POP'].astype(str)

# For *_NUM columns, convert to Int64 (nullable integer)
num_cols = ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
for col in num_cols:
    df[col] = df[col].astype('Int64')

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)