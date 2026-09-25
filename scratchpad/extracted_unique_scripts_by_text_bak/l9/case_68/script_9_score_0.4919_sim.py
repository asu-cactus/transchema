import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_4.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_9.csv", index_col=0)

union_df = pd.concat([df0, df2, df4, df9], ignore_index=True)

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_1.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_3.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_68/training_8.csv", index_col=0)

merged = union_df.merge(df1, on="ROW_WID", how="left")
merged = merged.merge(df3, on="ROW_WID", how="left")
merged = merged.merge(df5, on="ROW_WID", how="left")
merged = merged.merge(df6, on="ROW_WID", how="left")
merged = merged.merge(df7, on="ROW_WID", how="left")
merged = merged.merge(df8, on="ROW_WID", how="left")

cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = merged[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_68/target_multisource_mcts.csv", index=False)