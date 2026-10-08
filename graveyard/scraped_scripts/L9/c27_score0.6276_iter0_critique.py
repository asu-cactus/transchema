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

# UNION the four main tables with the same schema
main_union = pd.concat([source0, source2, source3, source9], ignore_index=True)

# Join the unioned main table with the other aspect tables on ROW_WID
# Use inner joins to avoid losing rows with missing keys (matches target row count)
df = main_union.merge(source1, on='ROW_WID', how='inner') \
               .merge(source4, on='ROW_WID', how='inner') \
               .merge(source5, on='ROW_WID', how='inner') \
               .merge(source6, on='ROW_WID', how='inner') \
               .merge(source7, on='ROW_WID', how='inner') \
               .merge(source8, on='ROW_WID', how='inner')

# Group by the leftmost unique key columns in target: ['CANCELED', 'ROW_WID', 'ACCNT_LOC']
# For aggregation:
# - For string columns and float columns, take first()
# - For *_NUM columns, sum()
# Columns to aggregate by first():
first_cols = ['ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP']
# Columns to sum:
sum_cols = ['COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

agg_dict = {col: 'first' for col in first_cols}
agg_dict.update({col: 'sum' for col in sum_cols})

grouped = df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_columns = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
                  'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
                  'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

grouped = grouped[target_columns]

# Write output
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv', index=False)