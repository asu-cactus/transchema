import pandas as pd
import numpy as np

# Read all source tables
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

# UNION the four dimension tables with the same schema
union_df = pd.concat([s0, s2, s3, s9], ignore_index=True)

# JOIN with aspect tables on ROW_WID using left joins to keep all rows from union_df
df = union_df.merge(s1, on="ROW_WID", how="left")
df = df.merge(s4, on="ROW_WID", how="left")
df = df.merge(s5, on="ROW_WID", how="left")
df = df.merge(s6, on="ROW_WID", how="left")
df = df.merge(s7, on="ROW_WID", how="left")
df = df.merge(s8, on="ROW_WID", how="left")

# Define group by columns (leftmost unique identifiers)
group_by_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'SES', 'CUST_SINCE_DT', 'CITY', 'POP']

# Define aggregation dictionary
agg_dict = {
    'ARPU': 'mean',
    'HOME_PASSED': 'mean',
    'MONTHS_AGE': 'mean',
    'CANCEL_DT': lambda x: x.dropna().min() if not x.dropna().empty else np.nan,
    'COLLECTION_EVENTS_NUM': 'sum',
    'INBOUND_CALLS_NUM': 'sum',
    'KEYWORDS_NUM': 'sum',
    'VISITS_NUM': 'sum',
    'TECHSUPPORT_NUM': 'sum',
    'INTERACTIONS_NUM': 'sum'
}

# Perform group by and aggregation
df_grouped = df.groupby(group_by_cols, dropna=False).agg(agg_dict).reset_index()

# Reorder columns to match target schema
final_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT',
              'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM',
              'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df_final = df_grouped[final_cols]

# Cast columns to target types
df_final['CANCELED'] = df_final['CANCELED'].astype('Int64')
df_final['ROW_WID'] = df_final['ROW_WID'].astype('Int64')
df_final['ACCNT_LOC'] = df_final['ACCNT_LOC'].astype('Int64')
df_final['ARPU'] = df_final['ARPU'].astype(float)
df_final['SES'] = df_final['SES'].astype(str)
df_final['HOME_PASSED'] = df_final['HOME_PASSED'].round().astype('Int64')  # mean rounded to int
df_final['CUST_SINCE_DT'] = df_final['CUST_SINCE_DT'].astype(str)
df_final['MONTHS_AGE'] = df_final['MONTHS_AGE'].astype(float)
df_final['CANCEL_DT'] = df_final['CANCEL_DT'].astype(str)
df_final['CITY'] = df_final['CITY'].astype(str)
df_final['POP'] = df_final['POP'].astype(str)
df_final['COLLECTION_EVENTS_NUM'] = df_final['COLLECTION_EVENTS_NUM'].fillna(0).astype('Int64')
df_final['INBOUND_CALLS_NUM'] = df_final['INBOUND_CALLS_NUM'].fillna(0).astype('Int64')
df_final['KEYWORDS_NUM'] = df_final['KEYWORDS_NUM'].fillna(0).astype('Int64')
df_final['VISITS_NUM'] = df_final['VISITS_NUM'].fillna(0).astype('Int64')
df_final['TECHSUPPORT_NUM'] = df_final['TECHSUPPORT_NUM'].fillna(0).astype('Int64')
df_final['INTERACTIONS_NUM'] = df_final['INTERACTIONS_NUM'].fillna(0).astype('Int64')

# Write to CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv", index=False)