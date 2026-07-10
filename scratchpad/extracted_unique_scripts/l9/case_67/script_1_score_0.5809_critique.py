import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv", index_col=0)

# UNION dimension tables with same schema
union_2_3_4_9 = pd.concat([s2, s3, s4, s9], ignore_index=True)

# JOIN aspect tables on ROW_WID using inner join to avoid duplicates and missing keys
join_0 = union_2_3_4_9.merge(s0, on="ROW_WID", how="inner")
join_1 = join_0.merge(s1, on="ROW_WID", how="inner")
join_2 = join_1.merge(s5, on="ROW_WID", how="inner")
join_3 = join_2.merge(s6, on="ROW_WID", how="inner")
join_4 = join_3.merge(s7, on="ROW_WID", how="inner")
join_5 = join_4.merge(s8, on="ROW_WID", how="inner")

# Define group by columns (leftmost non-float unique columns)
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'CUST_SINCE_DT', 'CITY', 'POP']

# Aggregations:
# mean for ARPU, HOME_PASSED, MONTHS_AGE
# first for CANCEL_DT (string)
# sum for count columns
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'mean',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': 'first',
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

# Perform group by and aggregation
result = join_5.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
target_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
               'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
               'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = result[target_cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)