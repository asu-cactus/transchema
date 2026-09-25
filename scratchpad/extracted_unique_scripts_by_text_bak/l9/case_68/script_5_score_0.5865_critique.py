import pandas as pd

# Read source tables with index_col=0 to ignore numerical index column
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv', index_col=0)
src4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv', index_col=0)
src5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv', index_col=0)
src6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv', index_col=0)
src7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv', index_col=0)
src8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv', index_col=0)
src9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv', index_col=0)

# UNION the base tables with same schema (first 11 columns)
base_union = pd.concat([src0, src2, src4, src9], ignore_index=True)

# Join aspect tables one by one on ROW_WID
# Use inner join to keep only rows present in base_union
df = base_union.merge(src1, on='ROW_WID', how='inner')
df = df.merge(src3, on='ROW_WID', how='inner')
df = df.merge(src5, on='ROW_WID', how='inner')
df = df.merge(src6, on='ROW_WID', how='inner')
df = df.merge(src7, on='ROW_WID', how='inner')
df = df.merge(src8, on='ROW_WID', how='inner')

# Group by leftmost non-float unique columns to remove duplicates from union
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Since no aggregation is specified, just drop duplicates by group keys keeping first
df = df.sort_values(by=group_by_cols).drop_duplicates(subset=group_by_cols, keep='first')

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[target_columns]

# Write output
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv', index=False)