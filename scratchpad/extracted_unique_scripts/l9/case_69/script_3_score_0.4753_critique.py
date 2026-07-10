import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv', index_col=0)

# UNION the 4 big tables with same schema
big_tables = pd.concat([source0, source1, source3, source4], ignore_index=True)

# Join all aspect tables on ROW_WID
# Start with big_tables
df = big_tables

# Join with source2 (KEYWORDS_NUM)
df = df.merge(source2, on='ROW_WID', how='left')

# Join with source5 (INTERACTIONS_NUM)
df = df.merge(source5, on='ROW_WID', how='left')

# Join with source6 (VISITS_NUM)
df = df.merge(source6, on='ROW_WID', how='left')

# Join with source7 (COLLECTION_EVENTS_NUM)
df = df.merge(source7, on='ROW_WID', how='left')

# Join with source8 (INBOUND_CALLS_NUM)
df = df.merge(source8, on='ROW_WID', how='left')

# Join with source9 (TECHSUPPORT_NUM)
df = df.merge(source9, on='ROW_WID', how='left')

# Now group by the leftmost non-float unique columns: CANCELED, ROW_WID, ACCNT_LOC
# Aggregations:
# ARPU, MONTHS_AGE: mean
# HOME_PASSED: sum (integer)
# SES, CUST_SINCE_DT, CANCEL_DT, CITY, POP: first (string)
# COLLECTION_EVENTS_NUM, INBOUND_CALLS_NUM, KEYWORDS_NUM, VISITS_NUM, TECHSUPPORT_NUM, INTERACTIONS_NUM: sum

agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'sum',
    'SES': 'first',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'mean',
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

grouped = df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# The target schema order is:
# ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
#  'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# HOME_PASSED was aggregated by sum, but it is an attribute, not a count. 
# From source data, HOME_PASSED is integer attribute, likely should be first or max, not sum.
# Correct HOME_PASSED aggregation to 'first' instead of 'sum'

# Fix aggregation for HOME_PASSED:
agg_dict['HOME_PASSED'] = 'first'

# Re-aggregate with corrected HOME_PASSED aggregation
grouped = df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Write output
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv', index=False)