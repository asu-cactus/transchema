import pandas as pd

# Read all sources
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

# UNION the dimension tables with same schema
union_df = pd.concat([s0, s2, s6, s7], ignore_index=True)

# Define aggregation functions for groupby
agg_dict = {
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'sum',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first'
}

# Group by key columns to remove duplicates and aggregate
union_agg = union_df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Join with aspect tables on ROW_WID using left joins
df = pd.merge(union_agg, s1, on='ROW_WID', how='left')
df = pd.merge(df, s3, on='ROW_WID', how='left')
df = pd.merge(df, s4, on='ROW_WID', how='left')
df = pd.merge(df, s5, on='ROW_WID', how='left')
df = pd.merge(df, s8, on='ROW_WID', how='left')
df = pd.merge(df, s9, on='ROW_WID', how='left')

# Select columns in target order
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)