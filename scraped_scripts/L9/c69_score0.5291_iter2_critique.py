import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv", index_col=0)

# UNION the four large tables with the same schema
union_result = pd.concat([s0, s1, s3, s4], ignore_index=True)

# JOIN union_result with all other aspect tables on ROW_WID
result = union_result.merge(s2, on="ROW_WID", how="left")
result = result.merge(s5, on="ROW_WID", how="left")
result = result.merge(s6, on="ROW_WID", how="left")
result = result.merge(s7, on="ROW_WID", how="left")
result = result.merge(s8, on="ROW_WID", how="left")
result = result.merge(s9, on="ROW_WID", how="left")

# Define aggregation functions for each column
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'mean',
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

# Group by the leftmost non-float unique columns as per hints
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES']

# Perform groupby and aggregation
final_df = result.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# The target schema columns in order
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Reorder columns to match target schema exactly
final_df = final_df[cols]

# Write to CSV without index
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv", index=False)