import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_24/training_9.csv", index_col=0)

union_df = pd.concat([src0, src2, src6, src7], ignore_index=True)

df = union_df.merge(src1, on="ROW_WID", how="left")
df = df.merge(src3, on="ROW_WID", how="left")
df = df.merge(src4, on="ROW_WID", how="left")
df = df.merge(src5, on="ROW_WID", how="left")
df = df.merge(src8, on="ROW_WID", how="left")
df = df.merge(src9, on="ROW_WID", how="left")

cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

df['ARPU'] = pd.to_numeric(df['ARPU'], errors='coerce')
df['MONTHS_AGE'] = pd.to_numeric(df['MONTHS_AGE'], errors='coerce')
df['CANCELED'] = pd.to_numeric(df['CANCELED'], errors='coerce').astype('Int64')
df['ROW_WID'] = pd.to_numeric(df['ROW_WID'], errors='coerce').astype('Int64')
df['ACCNT_LOC'] = pd.to_numeric(df['ACCNT_LOC'], errors='coerce').astype('Int64')
df['HOME_PASSED'] = pd.to_numeric(df['HOME_PASSED'], errors='coerce').astype('Int64')
df['COLLECTION_EVENTS_NUM'] = pd.to_numeric(df['COLLECTION_EVENTS_NUM'], errors='coerce').fillna(0).astype('Int64')
df['INBOUND_CALLS_NUM'] = pd.to_numeric(df['INBOUND_CALLS_NUM'], errors='coerce').fillna(0).astype('Int64')
df['KEYWORDS_NUM'] = pd.to_numeric(df['KEYWORDS_NUM'], errors='coerce').fillna(0).astype('Int64')
df['VISITS_NUM'] = pd.to_numeric(df['VISITS_NUM'], errors='coerce').fillna(0).astype('Int64')
df['TECHSUPPORT_NUM'] = pd.to_numeric(df['TECHSUPPORT_NUM'], errors='coerce').fillna(0).astype('Int64')
df['INTERACTIONS_NUM'] = pd.to_numeric(df['INTERACTIONS_NUM'], errors='coerce').fillna(0).astype('Int64')

df['SES'] = df['SES'].astype(str)
df['CUST_SINCE_DT'] = df['CUST_SINCE_DT'].astype(str)
df['CANCEL_DT'] = df['CANCEL_DT'].astype(str)
df['CITY'] = df['CITY'].astype(str)
df['POP'] = df['POP'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_24/target_multisource_mcts.csv", index=False)