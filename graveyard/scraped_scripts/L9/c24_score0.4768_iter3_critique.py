import pandas as pd

# Read all source tables with index_col=0
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv', index_col=0)

# UNION the four large-schema tables (Source0, Source2, Source6, Source7)
large_schema_tables = [source0, source2, source6, source7]
unioned_large = pd.concat(large_schema_tables, ignore_index=True)

# Join unioned large-schema table with all small tables on ROW_WID
# Use left join to keep all rows from unioned_large (dimension table)
df = unioned_large

# Define a helper function to join on ROW_WID
def join_on_row_wid(left, right):
    return pd.merge(left, right, on='ROW_WID', how='left')

df = join_on_row_wid(df, source1)  # KEYWORDS_NUM
df = join_on_row_wid(df, source3)  # VISITS_NUM
df = join_on_row_wid(df, source4)  # COLLECTION_EVENTS_NUM
df = join_on_row_wid(df, source5)  # TECHSUPPORT_NUM
df = join_on_row_wid(df, source8)  # INBOUND_CALLS_NUM
df = join_on_row_wid(df, source9)  # INTERACTIONS_NUM

# Now group by the leftmost non-float unique columns in target: ['CANCELED', 'ROW_WID', 'ACCNT_LOC']
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Aggregations:
# ARPU, MONTHS_AGE: mean
# HOME_PASSED: sum (integer measure)
# COLLECTION_EVENTS_NUM, INBOUND_CALLS_NUM, KEYWORDS_NUM, VISITS_NUM, TECHSUPPORT_NUM, INTERACTIONS_NUM: sum
# SES, CUST_SINCE_DT, CANCEL_DT, CITY, POP: first (string columns)

agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'sum',
    'MONTHS_AGE': 'mean',
    'SES': 'first',
    'CUST_SINCE_DT': 'first',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

# Some columns may have NaNs after join, sum aggregation will treat NaN as 0 by default if we fillna(0)
# But instructions say do NOT fill NaN with arbitrary constants except 0 if needed.
# So fill NaN in numeric columns with 0 before aggregation to avoid NaN sums.
numeric_cols_to_fill = ['HOME_PASSED', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
df[numeric_cols_to_fill] = df[numeric_cols_to_fill].fillna(0)

# Group by and aggregate
result = df.groupby(group_by_cols, as_index=False).agg(agg_dict)

# The group by dropped ACCNT_LOC from index, so ACCNT_LOC is preserved as column
# The target schema order is:
# ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
#  'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
                  'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = result[target_columns]

# Write to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv', index=False)