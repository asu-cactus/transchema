import pandas as pd

# Read source tables with index_col=0 to ignore the numerical index column
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

# UNION the four source tables with the same schema
unioned = pd.concat([source0, source2, source3, source9], ignore_index=True)

# JOIN unioned with all aspect tables on ROW_WID
df = unioned.merge(source1, on='ROW_WID', how='inner') \
             .merge(source4, on='ROW_WID', how='inner') \
             .merge(source5, on='ROW_WID', how='inner') \
             .merge(source6, on='ROW_WID', how='inner') \
             .merge(source7, on='ROW_WID', how='inner') \
             .merge(source8, on='ROW_WID', how='inner')

# GROUP BY the leftmost non-float unique columns in target schema
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']

# Aggregations:
# mean for ARPU, HOME_PASSED, MONTHS_AGE (numeric but not counts)
# sum for count-like columns
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'mean',
    'MONTHS_AGE': 'mean',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

result = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Write output to CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv', index=False)