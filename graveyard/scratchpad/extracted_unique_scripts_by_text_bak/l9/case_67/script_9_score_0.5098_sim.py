import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_67/training_9.csv", index_col=0)

union_df = pd.concat([s2, s3, s4, s9], ignore_index=True)

df = union_df.merge(s0, on="ROW_WID", how="left")
df = df.merge(s1, on="ROW_WID", how="left")
df = df.merge(s5, on="ROW_WID", how="left")
df = df.merge(s6, on="ROW_WID", how="left")
df = df.merge(s7, on="ROW_WID", how="left")
df = df.merge(s8, on="ROW_WID", how="left")

cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP',
        'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

df = df[cols]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)