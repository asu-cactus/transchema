import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv", index_col=0)

# Join dimension tables on ROW_WID
join_0 = pd.merge(s2, s3, on="ROW_WID", how="outer", suffixes=('_2', '_3'))
join_1 = pd.merge(join_0, s4, on="ROW_WID", how="outer", suffixes=('', '_4'))
join_2 = pd.merge(join_1, s9, on="ROW_WID", how="outer", suffixes=('', '_9'))

# Because columns like CANCELED, ACCNT_LOC, ARPU, SES, HOME_PASSED, CUST_SINCE_DT, MONTHS_AGE, CANCEL_DT, CITY, POP
# appear in all these tables, after merge they may have suffixes. We need to coalesce these columns to single columns.

def coalesce_columns(df, base_col):
    # Find all columns starting with base_col or base_col + suffix
    cols = [c for c in df.columns if c == base_col or c.startswith(base_col + '_')]
    # Coalesce by taking first non-null value row-wise
    df[base_col] = df[cols].bfill(axis=1).iloc[:, 0]
    # Drop the extra columns except base_col
    drop_cols = [c for c in cols if c != base_col]
    df.drop(columns=drop_cols, inplace=True)

# List of columns to coalesce (all columns from dimension tables except ROW_WID)
dim_cols = ['CANCELED', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP']
for col in dim_cols:
    coalesce_columns(join_2, col)

# Join with aspect tables on ROW_WID
join_3 = pd.merge(join_2, s0, on="ROW_WID", how="left")
join_4 = pd.merge(join_3, s1, on="ROW_WID", how="left")
join_5 = pd.merge(join_4, s5, on="ROW_WID", how="left")
join_6 = pd.merge(join_5, s6, on="ROW_WID", how="left")
join_7 = pd.merge(join_6, s7, on="ROW_WID", how="left")
final_join = pd.merge(join_7, s8, on="ROW_WID", how="left")

# Now group by primary key columns and aggregate
group_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Aggregations:
# ARPU, MONTHS_AGE: mean
# SES, CUST_SINCE_DT, CANCEL_DT, CITY, POP: first (string columns)
# HOME_PASSED, COLLECTION_EVENTS_NUM, INBOUND_CALLS_NUM, KEYWORDS_NUM, VISITS_NUM, TECHSUPPORT_NUM, INTERACTIONS_NUM: sum

agg_dict = {
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'sum',
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

# Some columns may have NaNs, sum will treat NaN as 0 by default if skipna=True, which is default.
# For safety, fill NaNs with 0 only for numeric columns before aggregation.

numeric_sum_cols = ['HOME_PASSED', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
final_join[numeric_sum_cols] = final_join[numeric_sum_cols].fillna(0)

# Group and aggregate
final_df = final_join.groupby(group_cols, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
final_df = final_df[['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                     'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                     'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']]

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)