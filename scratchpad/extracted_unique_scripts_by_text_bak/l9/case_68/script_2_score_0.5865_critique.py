import pandas as pd

# Read dimension tables (same schema)
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

# Union dimension tables
union_df = pd.concat([s0, s2, s4, s9], ignore_index=True)

# Read aspect tables
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)

# Join all aspect tables on ROW_WID using inner join to avoid extra rows
df = union_df.merge(s1, on="ROW_WID", how="inner") \
             .merge(s3, on="ROW_WID", how="inner") \
             .merge(s5, on="ROW_WID", how="inner") \
             .merge(s6, on="ROW_WID", how="inner") \
             .merge(s7, on="ROW_WID", how="inner") \
             .merge(s8, on="ROW_WID", how="inner")

# Define aggregation functions
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'mean',
    'MONTHS_AGE': 'mean',
    'SES': 'first',
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

# Group by key columns to remove duplicates and aggregate
final_df = df.groupby(['CANCELED', 'ROW_WID', 'ACCNT_LOC'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
        'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
        'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
final_df = final_df[cols]

# Cast columns to correct types
final_df['CANCELED'] = final_df['CANCELED'].astype('Int64')
final_df['ROW_WID'] = final_df['ROW_WID'].astype('Int64')
final_df['ACCNT_LOC'] = final_df['ACCNT_LOC'].astype('Int64')
final_df['ARPU'] = final_df['ARPU'].astype(float)
final_df['HOME_PASSED'] = final_df['HOME_PASSED'].astype('Int64')
final_df['MONTHS_AGE'] = final_df['MONTHS_AGE'].astype(float)
final_df['COLLECTION_EVENTS_NUM'] = final_df['COLLECTION_EVENTS_NUM'].astype('Int64')
final_df['INBOUND_CALLS_NUM'] = final_df['INBOUND_CALLS_NUM'].astype('Int64')
final_df['KEYWORDS_NUM'] = final_df['KEYWORDS_NUM'].astype('Int64')
final_df['VISITS_NUM'] = final_df['VISITS_NUM'].astype('Int64')
final_df['TECHSUPPORT_NUM'] = final_df['TECHSUPPORT_NUM'].astype('Int64')
final_df['INTERACTIONS_NUM'] = final_df['INTERACTIONS_NUM'].astype('Int64')

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)