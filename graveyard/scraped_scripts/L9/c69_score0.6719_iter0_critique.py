import pandas as pd

# Read source tables with index_col=0 to ignore the numerical index column
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv', index_col=0)
src4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv', index_col=0)
src5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv', index_col=0)
src6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv', index_col=0)
src7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv', index_col=0)
src8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv', index_col=0)
src9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv', index_col=0)

# UNION the dimension tables (sources with same schema)
dim_union = pd.concat([src0, src1, src3, src4], ignore_index=True)

# Join the unioned dimension table with each aspect table on ROW_WID using inner join
df = dim_union.merge(src2, on='ROW_WID', how='inner') \
              .merge(src5, on='ROW_WID', how='inner') \
              .merge(src6, on='ROW_WID', how='inner') \
              .merge(src7, on='ROW_WID', how='inner') \
              .merge(src8, on='ROW_WID', how='inner') \
              .merge(src9, on='ROW_WID', how='inner')

# Group by the leftmost non-float unique columns to ensure uniqueness and match target row count
# According to target schema and hints, group by ['CANCELED', 'ROW_WID', 'ACCNT_LOC']
# No aggregation needed, just drop duplicates if any
df = df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).first()

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[target_columns]

# Write output
df.to_csv('autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv', index=False)