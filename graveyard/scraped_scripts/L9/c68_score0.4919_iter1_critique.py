import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

# UNION the tables with the same schema
union_df = pd.concat([s0, s2, s4, s9], ignore_index=True)

# JOIN with other tables on ROW_WID
df = union_df.merge(s1, on="ROW_WID", how="left") \
             .merge(s3, on="ROW_WID", how="left") \
             .merge(s5, on="ROW_WID", how="left") \
             .merge(s6, on="ROW_WID", how="left") \
             .merge(s7, on="ROW_WID", how="left") \
             .merge(s8, on="ROW_WID", how="left")

# Define group by columns (leftmost non-float unique columns)
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'CANCEL_DT', 'CITY', 'POP']

# Define aggregation dictionary
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
final_df = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema
cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']
final_df = final_df[cols]

# Cast columns to correct types
final_df['ARPU'] = final_df['ARPU'].astype(float)
final_df['MONTHS_AGE'] = final_df['MONTHS_AGE'].astype(float)
final_df['CANCELED'] = final_df['CANCELED'].astype('Int64')
final_df['ROW_WID'] = final_df['ROW_WID'].astype('Int64')
final_df['ACCNT_LOC'] = final_df['ACCNT_LOC'].astype('Int64')
final_df['HOME_PASSED'] = final_df['HOME_PASSED'].astype('Int64')
final_df['COLLECTION_EVENTS_NUM'] = final_df['COLLECTION_EVENTS_NUM'].astype('Int64')
final_df['INBOUND_CALLS_NUM'] = final_df['INBOUND_CALLS_NUM'].astype('Int64')
final_df['KEYWORDS_NUM'] = final_df['KEYWORDS_NUM'].astype('Int64')
final_df['VISITS_NUM'] = final_df['VISITS_NUM'].astype('Int64')
final_df['TECHSUPPORT_NUM'] = final_df['TECHSUPPORT_NUM'].astype('Int64')
final_df['INTERACTIONS_NUM'] = final_df['INTERACTIONS_NUM'].astype('Int64')

# Write to output CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)