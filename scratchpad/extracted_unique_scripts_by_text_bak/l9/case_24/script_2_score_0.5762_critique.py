import pandas as pd

# Read all source tables with index_col=0 as per Hint 22
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

# UNION the dimension tables (same schema)
dim_tables = [source0, source2, source6, source7]
unioned_dim = pd.concat(dim_tables, ignore_index=True)

# Join the unioned dimension table with all aspect tables on ROW_WID
# Use inner join to keep only matching ROW_WID (consistent with target row count)
df = unioned_dim.merge(source1, on='ROW_WID', how='inner') \
                 .merge(source3, on='ROW_WID', how='inner') \
                 .merge(source4, on='ROW_WID', how='inner') \
                 .merge(source5, on='ROW_WID', how='inner') \
                 .merge(source8, on='ROW_WID', how='inner') \
                 .merge(source9, on='ROW_WID', how='inner')

# Group by ROW_WID to remove duplicates and ensure uniqueness
# Since ROW_WID is unique key, group by ROW_WID and take first for non-numeric columns,
# sum or mean for numeric columns if needed. Here, no aggregation needed except removing duplicates.
df = df.groupby('ROW_WID', as_index=False).first()

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[target_columns]

# Write output
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv', index=False)