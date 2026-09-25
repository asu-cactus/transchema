import pandas as pd

# Read source tables with index_col=0 as per hint 22
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_27/training_9.csv', index_col=0)

# UNION the four dimension tables (source0, source2, source3, source9)
dim_tables = [source0, source2, source3, source9]
dim_union = pd.concat(dim_tables, ignore_index=True)

# Join the unioned dimension table with all aspect tables on ROW_WID
# Start with dim_union
df = dim_union

# Join with source1 (COLLECTION_EVENTS_NUM)
df = df.merge(source1, on='ROW_WID', how='left')

# Join with source4 (INBOUND_CALLS_NUM)
df = df.merge(source4, on='ROW_WID', how='left')

# Join with source5 (VISITS_NUM)
df = df.merge(source5, on='ROW_WID', how='left')

# Join with source6 (INTERACTIONS_NUM)
df = df.merge(source6, on='ROW_WID', how='left')

# Join with source7 (KEYWORDS_NUM)
df = df.merge(source7, on='ROW_WID', how='left')

# Join with source8 (TECHSUPPORT_NUM)
df = df.merge(source8, on='ROW_WID', how='left')

# Now group by ['CANCELED', 'ROW_WID', 'ACCNT_LOC']
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Define aggregation dictionary
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'sum',
    'MONTHS_AGE': 'mean',
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

# Some columns may have NaN after join, fill NaN in numeric columns with 0 before aggregation sums
numeric_sum_cols = ['HOME_PASSED', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
for col in numeric_sum_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# For ARPU and MONTHS_AGE (mean), NaNs will be ignored by mean aggregation

# Perform groupby aggregation
result = df.groupby(group_by_cols).agg(agg_dict).reset_index()

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Some columns may be missing if source tables had no data, ensure all columns exist
for col in target_columns:
    if col not in result.columns:
        # Add missing columns with NaN or 0 for numeric sums
        if col in numeric_sum_cols + ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']:
            result[col] = 0
        else:
            result[col] = pd.NA

result = result[target_columns]

# Write to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv', index=False)