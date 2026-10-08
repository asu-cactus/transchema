import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv", index_col=0)

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv", index_col=0)

# Join the four large source tables on ROW_WID
join_01 = pd.merge(df0, df1, on='ROW_WID', how='inner', suffixes=('_0', '_1'))
join_013 = pd.merge(join_01, df3, on='ROW_WID', how='inner', suffixes=('', '_3'))
join_0134 = pd.merge(join_013, df4, on='ROW_WID', how='inner', suffixes=('', '_4'))

# After joining, columns from df0, df1, df3, df4 may have duplicates due to same column names.
# We need to resolve columns by choosing one representative column per attribute.
# Since these tables have the same schema, pick columns from df0 and fill missing with others.

# Define a helper function to coalesce columns from multiple suffixes
def coalesce_columns(df, base_col, suffixes):
    for suffix in suffixes:
        col = base_col + suffix
        if col in df.columns:
            df[base_col] = df[base_col].combine_first(df[col])
            df.drop(columns=[col], inplace=True)
    return df

# List of columns to coalesce (all except ROW_WID)
cols = ['CANCELED', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP']

for col in cols:
    # Suffixes from df1, df3, df4
    join_0134 = coalesce_columns(join_0134, col, ['_0', '_1', '_3', '_4'])

# Now join with the other aspect tables on ROW_WID using left joins to keep only rows present in the main dimension
df = join_0134
df = pd.merge(df, df2, on='ROW_WID', how='left')
df = pd.merge(df, df5, on='ROW_WID', how='left')
df = pd.merge(df, df6, on='ROW_WID', how='left')
df = pd.merge(df, df7, on='ROW_WID', how='left')
df = pd.merge(df, df8, on='ROW_WID', how='left')
df = pd.merge(df, df9, on='ROW_WID', how='left')

# Group by the leftmost unique columns: 'CANCELED', 'ROW_WID', 'ACCNT_LOC'
# Aggregations:
# - mean for float columns: ARPU, MONTHS_AGE
# - sum for count columns: HOME_PASSED, COLLECTION_EVENTS_NUM, INBOUND_CALLS_NUM, KEYWORDS_NUM, VISITS_NUM, TECHSUPPORT_NUM, INTERACTIONS_NUM
# - first for string/date columns: SES, CUST_SINCE_DT, CANCEL_DT, CITY, POP

agg_dict = {
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean',
    'HOME_PASSED': 'sum',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum',
    'SES': 'first',
    'CUST_SINCE_DT': 'first',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first'
}

# Some columns may have NaNs, sum will treat NaN as 0 by default in pandas >=1.1.0, but to be safe fill NaN with 0 for sum columns before aggregation
sum_cols = ['HOME_PASSED', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
df[sum_cols] = df[sum_cols].fillna(0)

grouped = df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
final_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
              'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

final_df = grouped[final_cols]

# Write to CSV without index
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv", index=False)