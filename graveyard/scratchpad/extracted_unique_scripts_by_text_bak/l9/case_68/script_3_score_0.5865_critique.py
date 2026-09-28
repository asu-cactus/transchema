import pandas as pd

# Read all source CSVs with index_col=0
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

# UNION dimension tables (src0, src2, src4, src9)
dim_tables = [src0, src2, src4, src9]
dim_union = pd.concat(dim_tables, ignore_index=True)

# Join dimension union with aspect tables on ROW_WID
# Start with dim_union as base
df = dim_union

# Join with src1 (TECHSUPPORT_NUM)
df = df.merge(src1, on='ROW_WID', how='inner')

# Join with src3 (VISITS_NUM)
df = df.merge(src3, on='ROW_WID', how='inner')

# Join with src5 (KEYWORDS_NUM)
df = df.merge(src5, on='ROW_WID', how='inner')

# Join with src6 (INBOUND_CALLS_NUM)
df = df.merge(src6, on='ROW_WID', how='inner')

# Join with src7 (INTERACTIONS_NUM)
df = df.merge(src7, on='ROW_WID', how='inner')

# Join with src8 (COLLECTION_EVENTS_NUM)
df = df.merge(src8, on='ROW_WID', how='inner')

# Define group by columns (leftmost non-float unique columns)
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']

# Aggregations:
# ARPU and MONTHS_AGE: mean
# *_NUM columns: sum
agg_dict = {
    'ARPU': 'mean',
    'MONTHS_AGE': 'mean',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

# Perform group by and aggregation
result = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED',
                  'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
                  'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM',
                  'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = result[target_columns]

# Write to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv', index=False)