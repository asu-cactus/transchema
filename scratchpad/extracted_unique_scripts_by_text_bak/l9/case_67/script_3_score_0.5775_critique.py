import pandas as pd

# Read all source CSVs with index_col=0 to ignore numerical index column
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv', index_col=0)
source2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv', index_col=0)
source3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv', index_col=0)
source4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv', index_col=0)
source5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv', index_col=0)
source6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv', index_col=0)
source7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv', index_col=0)
source8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv', index_col=0)
source9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv', index_col=0)

# UNION dimension tables (Source2, Source3, Source4, Source9) - same schema
dim_union = pd.concat([source2, source3, source4, source9], ignore_index=True)

# Join dimension union with Source0 (COLLECTION_EVENTS_NUM)
df = pd.merge(dim_union, source0, on='ROW_WID', how='inner')

# Join with Source1 (INTERACTIONS_NUM)
df = pd.merge(df, source1, on='ROW_WID', how='inner')

# Join with Source5 (INBOUND_CALLS_NUM)
df = pd.merge(df, source5, on='ROW_WID', how='inner')

# Join with Source6 (KEYWORDS_NUM)
df = pd.merge(df, source6, on='ROW_WID', how='inner')

# Join with Source7 (TECHSUPPORT_NUM)
df = pd.merge(df, source7, on='ROW_WID', how='inner')

# Join with Source8 (VISITS_NUM)
df = pd.merge(df, source8, on='ROW_WID', how='inner')

# Group by leftmost unique keys to ensure uniqueness and match target row count
group_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Since no aggregation is specified, just drop duplicates on group_cols to ensure uniqueness
df = df.drop_duplicates(subset=group_cols)

# Reorder columns to match target schema exactly
target_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
               'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
               'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[target_cols]

# Write output CSV
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv', index=False)