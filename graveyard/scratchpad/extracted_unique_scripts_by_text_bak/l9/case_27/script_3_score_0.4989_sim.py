import pandas as pd

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

union_df = pd.concat([s0, s2, s3, s9], ignore_index=True)

df = union_df.merge(s1, on="ROW_WID", how="left")
df = df.merge(s4, on="ROW_WID", how="left")
df = df.merge(s5, on="ROW_WID", how="left")
df = df.merge(s6, on="ROW_WID", how="left")
df = df.merge(s7, on="ROW_WID", how="left")
df = df.merge(s8, on="ROW_WID", how="left")

df = df[['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
         'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']]

df['CANCELED'] = df['CANCELED'].astype('Int64')
df['ROW_WID'] = df['ROW_WID'].astype('Int64')
df['ACCNT_LOC'] = df['ACCNT_LOC'].astype('Int64')
df['ARPU'] = df['ARPU'].astype(float)
df['SES'] = df['SES'].astype(str)
df['HOME_PASSED'] = df['HOME_PASSED'].astype('Int64')
df['CUST_SINCE_DT'] = df['CUST_SINCE_DT'].astype(str)
df['MONTHS_AGE'] = df['MONTHS_AGE'].astype(float)
df['CANCEL_DT'] = df['CANCEL_DT'].astype(str)
df['CITY'] = df['CITY'].astype(str)
df['POP'] = df['POP'].astype(str)
df['COLLECTION_EVENTS_NUM'] = df['COLLECTION_EVENTS_NUM'].astype('Int64')
df['INBOUND_CALLS_NUM'] = df['INBOUND_CALLS_NUM'].astype('Int64')
df['KEYWORDS_NUM'] = df['KEYWORDS_NUM'].astype('Int64')
df['VISITS_NUM'] = df['VISITS_NUM'].astype('Int64')
df['TECHSUPPORT_NUM'] = df['TECHSUPPORT_NUM'].astype('Int64')
df['INTERACTIONS_NUM'] = df['INTERACTIONS_NUM'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_27/target_multisource_mcts.csv", index=False)