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

union_2_3_4_9 = pd.concat([s2, s3, s4, s9], ignore_index=True)

join_0 = union_2_3_4_9.merge(s0, on="ROW_WID", how="left")
join_1 = join_0.merge(s1, on="ROW_WID", how="left")
join_2 = join_1.merge(s5, on="ROW_WID", how="left")
join_3 = join_2.merge(s6, on="ROW_WID", how="left")
join_4 = join_3.merge(s7, on="ROW_WID", how="left")
join_5 = join_4.merge(s8, on="ROW_WID", how="left")

target_cols = ['CANCELED', 'ROW_WID', 'ACCNT_LOC', 'ARPU', 'SES', 'HOME_PASSED', 'CUST_SINCE_DT', 'MONTHS_AGE', 'CANCEL_DT', 'CITY', 'POP', 'COLLECTION_EVENTS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM', 'VISITS_NUM', 'TECHSUPPORT_NUM', 'INTERACTIONS_NUM']

result = join_5[target_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_67/target_multisource_mcts.csv", index=False)