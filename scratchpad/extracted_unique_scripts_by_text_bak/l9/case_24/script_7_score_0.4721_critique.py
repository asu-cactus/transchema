import pandas as pd

# Read all source files
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

# UNION the dimension tables with the same schema
union_df = pd.concat([s0, s2, s6, s7], ignore_index=True)

# JOIN the unioned dimension table with all aspect tables on ROW_WID using left join to keep all dimension rows
df = union_df.merge(s1, on="ROW_WID", how="left")
df = df.merge(s3, on="ROW_WID", how="left")
df = df.merge(s4, on="ROW_WID", how="left")
df = df.merge(s5, on="ROW_WID", how="left")
df = df.merge(s8, on="ROW_WID", how="left")
df = df.merge(s9, on="ROW_WID", how="left")

# Define aggregation functions
agg_dict = {
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'first',
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

# Group by the leftmost non-float unique columns
group_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC']

# Perform group by and aggregation to remove duplicates and aggregate counts/means
df = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df = df[['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
         'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
         'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)