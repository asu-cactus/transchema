import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
source_0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv', index_col=0)
source_1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv', index_col=0)
source_2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv', index_col=0)
source_3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv', index_col=0)
source_4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv', index_col=0)
source_5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv', index_col=0)
source_6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv', index_col=0)
source_7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv', index_col=0)
source_8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv', index_col=0)
source_9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv', index_col=0)

# UNION the dimension tables (Source9_67_2, 3, 4, 9)
dim_tables = [source_2, source_3, source_4, source_9]
unioned_dim = pd.concat(dim_tables, ignore_index=True)

# Join unioned_dim with all aspect tables on ROW_WID
# Start with unioned_dim joined with source_0
result = pd.merge(unioned_dim, source_0, on='ROW_WID', how='inner')

# Join with source_1
result = pd.merge(result, source_1, on='ROW_WID', how='inner')

# Join with source_5
result = pd.merge(result, source_5, on='ROW_WID', how='inner')

# Join with source_6
result = pd.merge(result, source_6, on='ROW_WID', how='inner')

# Join with source_7
result = pd.merge(result, source_7, on='ROW_WID', how='inner')

# Join with source_8
result = pd.merge(result, source_8, on='ROW_WID', how='inner')

# Group by the leftmost non-float unique columns in target schema
# According to target schema and hints: ['CANCELED', 'ROW_WID', 'ACCNT_LOC']
group_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Since no aggregation columns specified, just drop duplicates by group_cols to ensure uniqueness
result = result.drop_duplicates(subset=group_cols)

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Some columns come from different tables, ensure all columns exist
# If any columns missing due to join, they will be NaN, which is allowed per hint 24

result = result[target_columns]

# Write to output CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv', index=False)