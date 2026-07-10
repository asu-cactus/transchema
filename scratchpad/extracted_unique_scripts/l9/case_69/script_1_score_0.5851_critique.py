import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv", index_col=0)

# UNION the four main tables with the same schema
union_result = pd.concat([s0, s1, s3, s4], ignore_index=True)

# Read aspect tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv", index_col=0)

# Perform INNER joins on ROW_WID to keep only matching rows
join_result_1 = pd.merge(union_result, s2, on="ROW_WID", how="inner")
join_result_2 = pd.merge(join_result_1, s5, on="ROW_WID", how="inner")
join_result_3 = pd.merge(join_result_2, s6, on="ROW_WID", how="inner")
join_result_4 = pd.merge(join_result_3, s7, on="ROW_WID", how="inner")
join_result_5 = pd.merge(join_result_4, s8, on="ROW_WID", how="inner")
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="inner")

# Define aggregation functions:
# For string columns, take first (assuming consistent per group)
# For float columns (ARPU, MONTHS_AGE), take mean
# For integer count columns, take sum

agg_dict = {
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'sum',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'mean',
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

# Group by the leftmost unique key columns
group_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Perform groupby and aggregation
final_df = final_join.groupby(group_cols, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

final_df = final_df[cols]

# Write to CSV without index
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv", index=False)