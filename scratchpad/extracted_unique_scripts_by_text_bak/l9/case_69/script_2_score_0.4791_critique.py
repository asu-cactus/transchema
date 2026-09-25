import pandas as pd

# Read the four large tables with the same schema
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_4.csv", index_col=0)

# UNION the four large tables
union_result = pd.concat([s0, s1, s3, s4], ignore_index=True)

# Read aspect tables
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_2.csv", index_col=0)  # KEYWORDS_NUM
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_5.csv", index_col=0)  # INTERACTIONS_NUM
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_6.csv", index_col=0)  # VISITS_NUM
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_7.csv", index_col=0)  # COLLECTION_EVENTS_NUM
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_8.csv", index_col=0)  # INBOUND_CALLS_NUM
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_69/training_9.csv", index_col=0)  # TECHSUPPORT_NUM

# Join aspect tables one by one on ROW_WID with left join to keep all rows from union_result
join_result_1 = pd.merge(union_result, s2, on="ROW_WID", how="left")
join_result_2 = pd.merge(join_result_1, s5, on="ROW_WID", how="left")
join_result_3 = pd.merge(join_result_2, s6, on="ROW_WID", how="left")
join_result_4 = pd.merge(join_result_3, s7, on="ROW_WID", how="left")
join_result_5 = pd.merge(join_result_4, s8, on="ROW_WID", how="left")
final_join = pd.merge(join_result_5, s9, on="ROW_WID", how="left")

# Define group by columns (leftmost non-float unique columns)
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']

# Aggregation dictionary:
# mean for float columns ARPU and MONTHS_AGE
# sum for *_NUM columns (integer counts)
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
final_df = final_join.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# The target schema order:
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

# Reorder columns to match target schema
final_df = final_df[cols]

# Write to CSV without index
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_69/target_multisource_mcts.csv", index=False)