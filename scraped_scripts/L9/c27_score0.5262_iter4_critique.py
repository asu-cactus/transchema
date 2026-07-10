import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_27/training_9.csv", index_col=0)

# UNION the four main tables with same schema
union_df = pd.concat([s0, s2, s3, s9], ignore_index=True)

# Define aggregation dictionary for groupby
agg_dict = {
    'ARPU': 'mean',
    'SES': 'first',
    'HOME_PASSED': 'mean',
    'CUST_SINCE_DT': 'first',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': 'first',
    'CITY': 'first',
    'POP': 'first'
}

# Group by key columns with aggregations
grouped = union_df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Join with aspect tables on ROW_WID
df = grouped.merge(s1, on='ROW_WID', how='left')
df = df.merge(s4, on='ROW_WID', how='left')
df = df.merge(s5, on='ROW_WID', how='left')
df = df.merge(s6, on='ROW_WID', how='left')
df = df.merge(s7, on='ROW_WID', how='left')
df = df.merge(s8, on='ROW_WID', how='left')

# Round HOME_PASSED to int because it is integer in target schema
df['HOME_PASSED'] = df['HOME_PASSED'].round().astype('Int64')

# Select columns in target order
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv", index=False)