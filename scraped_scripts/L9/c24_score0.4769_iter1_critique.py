import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)

# UNION the four large source tables with the same schema
union_df = pd.concat([s0, s2, s6, s7], ignore_index=True)

# JOIN with all other aspect tables on ROW_WID using left joins
df = union_df.merge(s1, on="ROW_WID", how="left") \
             .merge(s3, on="ROW_WID", how="left") \
             .merge(s4, on="ROW_WID", how="left") \
             .merge(s5, on="ROW_WID", how="left") \
             .merge(s8, on="ROW_WID", how="left") \
             .merge(s9, on="ROW_WID", how="left")

# Define group by keys
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES']

# Aggregate functions mapping
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'mean',
    'MONTHS_AGE': 'mean',
    'CUST_SINCE_DT': 'first',
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

# Perform group by and aggregation
result = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
final_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED',
              'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
              'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM',
              'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = result[final_cols]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)