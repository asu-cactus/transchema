import pandas as pd

# Read all source CSVs with index_col=0
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv', index_col=0)
src4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv', index_col=0)
src5 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv', index_col=0)
src6 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv', index_col=0)
src7 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv', index_col=0)
src8 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv', index_col=0)
src9 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv', index_col=0)

# UNION dimension tables (src2, src3, src4, src9) - same schema
dim = pd.concat([src2, src3, src4, src9], ignore_index=True)

# Join dimension table with aspect tables on ROW_WID
# Start join with src0
df = dim.merge(src0, on='ROW_WID', how='inner')

# Join with src1
df = df.merge(src1, on='ROW_WID', how='inner')

# Join with src5
df = df.merge(src5, on='ROW_WID', how='inner')

# Join with src6
df = df.merge(src6, on='ROW_WID', how='inner')

# Join with src7
df = df.merge(src7, on='ROW_WID', how='inner')

# Join with src8
df = df.merge(src8, on='ROW_WID', how='inner')

# Group by leftmost non-float unique columns: 'CANCELED', 'ROW_WID', 'ACCNT_LOC'
# Aggregations:
# - For numeric columns that are counts or sums: sum
# - For categorical/string columns: take first (assuming consistent per group)
# - For float columns like ARPU and MONTHS_AGE: sum (based on hint 13, average is not target)
# - For date/string columns: first

agg_dict = {
    'ARPU': 'sum',
    'SES': 'first',
    'HOME_PASSED': 'sum',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'sum',
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

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Some columns might be missing if no data, ensure all columns exist
for col in target_columns:
    if col not in grouped.columns:
        grouped[col] = pd.NA

grouped = grouped[target_columns]

# Write output CSV
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv', index=False)